<template>
	<view class="page">

		<scroll-view class="list" scroll-y :scroll-into-view="scrollAnchor" scroll-with-animation>

			<!-- 空状态：给几个能直接点的示例。
			     空白对话框是最劝退的东西，用户不知道该说什么、也不知道这东西能干什么。
			     第二个示例专门走合规检查那条路，一点就能看到商标风险条目。 -->
			<view v-if="!messages.length" class="empty">
				<text class="empty-h">品牌／产品取名</text>
				<text class="empty-p">告诉我品类和调性，我来出名字；也可以直接甩一个名字给我，我帮你查商标法上的风险。</text>
				<view class="chips">
					<view v-for="(s, i) in suggestions" :key="i" class="chip" @click="useSuggestion(s)">
						<text class="chip-t">{{ s }}</text>
					</view>
				</view>
			</view>

			<view v-for="(m, i) in messages" :key="i" :class="['row', m.role === 'user' ? 'row-r' : 'row-l']">

				<!-- 用户 -->
				<view v-if="m.role === 'user'" class="bub bub-u">{{ m.text }}</view>

				<!-- 等待中：显示后端推来的真进度 -->
				<view v-else-if="m.kind === 'loading'" class="bub bub-a loading">
					<view class="dots"><view class="dot"></view><view class="dot"></view><view class="dot"></view></view>
					<text class="stage">{{ m.stageText }}</text>
				</view>

				<!-- 澄清中 -->
				<view v-else-if="m.kind === 'ask'" class="bub bub-a">
					<text class="ask">{{ m.text }}</text>
				</view>

				<!-- 失败 -->
				<view v-else-if="m.kind === 'error'" class="bub bub-a bub-err">
					<text class="err-t">{{ m.text }}</text>
				</view>

				<!-- 正常／降级：名字卡片 -->
				<view v-else class="bub bub-a cards">
					<view v-for="(c, ci) in m.candidates" :key="ci" class="ncard">
						<view class="nrow">
							<text class="nname">{{ c.name }}</text>
							<text v-if="c.origin === '用户提供'" class="ntag">你提的</text>
						</view>
						<text v-if="c.meaning" class="nmean">{{ c.meaning }}</text>
						<view v-if="c.source" class="nsrc">
							<view class="nsrc-bar"></view>
							<text class="nsrc-t">{{ c.source }}</text>
						</view>

						<!-- risks 是两层：条款 -> 多条理由。默认收起，点一下展开 -->
						<view v-if="c.risks && c.risks.length" class="risk" @click="toggle(i, ci)">
							<view class="risk-h">
								<text class="risk-n">{{ c.risks.length }}</text>
								<text class="risk-l">条商标风险</text>
								<text class="risk-more">{{ isOpen(i, ci) ? '收起' : '展开' }}</text>
							</view>
							<view v-if="isOpen(i, ci)" class="risk-b">
								<view v-for="(r, ri) in c.risks" :key="ri" class="ritem">
									<view class="rrow">
										<text class="rclause">{{ r.clause_number }}</text>
										<text :class="['rgrade', gradeClass(r.risk_grade)]">{{ r.risk_grade }}</text>
									</view>
									<text class="rlaw">{{ r.law_name }} · {{ r.law_version_name }}</text>
									<view v-for="(rs, rsi) in r.reasons" :key="rsi" class="reason">
										<text :class="['rtag', rs.judged_by === '系统扫描' ? 'rtag-rule' : 'rtag-ai']">{{ rs.judged_by }}</text>
										<text class="rtext">{{ rs.text }}</text>
									</view>
								</view>
							</view>
						</view>
					</view>
					<text v-if="m.disclaimer" class="disc">{{ m.disclaimer }}</text>
				</view>
			</view>

			<view id="bottom" class="pad"></view>
		</scroll-view>

		<!-- 输入区：只有一个输入框。
		     这里不许长出「候选名」「品类」「调性」这类分格输入框，
		     长出即表单版回潮，对话版就没意义了。 -->
		<view class="bar">
			<input
				class="ipt"
				v-model="draft"
				:disabled="busy"
				placeholder="说点什么，比如「茶叶，想要清雅一点的」"
				placeholder-class="ph"
				confirm-type="send"
				@confirm="send"
			/>
			<view v-if="!busy" :class="['sbtn', draft.trim() ? '' : 'sbtn-off']" @click="send">
				<text class="sbtn-t">↑</text>
			</view>
			<view v-else class="sbtn sbtn-stop" @click="stop">
				<text class="sbtn-t">■</text>
			</view>
		</view>

		<view class="foot">
			<text class="foot-l" @click="goBack">← 功能选择</text>
			<text class="foot-r" @click="newChat">开新对话</text>
		</view>
	</view>
</template>

<script setup>
import { ref, nextTick, onMounted, onUnmounted } from "vue"
import API, { chatStream } from "../../common/api.js"

// conversation_id 存本地：这决定了「刷新页面之后还能不能接着聊」。
// 存页面变量的话刷新就没了，只能开新对话。
const STORAGE_KEY = "chat_conversation_id"

// 空状态的示例问题。第二个走合规检查，能看到风险条目长什么样
const suggestions = [
	"帮我想几个茶叶品牌名，要清雅一点的",
	"「中国红」这个名字用在茶叶上能不能注册",
	"给一个宠物食品品牌起名，年轻一点",
	"我要做个 SaaS 产品，帮我想几个名字"
]

const messages = ref([])
const draft = ref("")
const busy = ref(false)
const conversationId = ref(null)
const opened = ref({})
const scrollAnchor = ref("")
let controller = null

const scrollToBottom = () => { nextTick(() => { scrollAnchor.value = "bottom" }) }
const lastMsg = () => messages.value[messages.value.length - 1]

// 风险条目默认收起。key 用「消息下标-候选名下标」，因为同一条消息里有多个名字
const kOf = (i, ci) => i + "-" + ci
const isOpen = (i, ci) => !!opened.value[kOf(i, ci)]
const toggle = (i, ci) => {
	const k = kOf(i, ci)
	opened.value = Object.assign({}, opened.value, { [k]: !opened.value[k] })
}

const gradeClass = (g) => g === "禁止使用" ? "g-ban" : (g === "不予注册" ? "g-ref" : "g-exc")

const useSuggestion = (s) => {
	draft.value = s
	send()
}

// status 四态 -> 界面三种样子：
//   澄清中 -> 反问气泡    失败 -> 提示    正常／降级 -> 名字卡片
// 正常和降级画得一模一样：后端 AgentSchema 的校验规定降级时 user_message 必须是 null，
// 所以没地方放「这次是降级结果」这句话。要让降级可见得改后端结构，这一版先不做。
const roundToMessage = (status, reply, disclaimer) => {
	const r = reply || {}
	if (status === "失败") {
		return { role: "assistant", kind: "error", text: r.user_message || "这次没能生成结果，请重试一次" }
	}
	if (status === "澄清中") {
		return { role: "assistant", kind: "ask", text: r.user_message || "" }
	}
	return { role: "assistant", kind: "names", candidates: r.candidates || [], disclaimer: disclaimer || "" }
}

// 刷新页面后重画历史。只有本地还留着 conversation_id 时才调
const loadHistory = async () => {
	let cid = null
	try { cid = uni.getStorageSync(STORAGE_KEY) } catch (e) {}
	if (!cid) return
	try {
		const data = await API.chatHistory(cid)
		conversationId.value = data.conversation_id
		const list = []
		;(data.rounds || []).forEach((rd) => {
			list.push({ role: "user", text: rd.user_input })
			list.push(roundToMessage(rd.status, rd.reply, data.disclaimer))
		})
		messages.value = list
		scrollToBottom()
	} catch (e) {
		// 会话可能已经不存在了（后端换了库、或者被清了）。
		// 必须把本地 id 清掉，否则每次进页面都会白失败一次
		try { uni.removeStorageSync(STORAGE_KEY) } catch (err) {}
		conversationId.value = null
	}
}

const send = () => {
	const text = draft.value.trim()
	if (!text || busy.value) return
	// 后端 ChatIn 限了 1~500 字，前端先拦一道省一次往返
	if (text.length > 500) {
		uni.showToast({ title: "一次最多 500 字", icon: "none" })
		return
	}
	draft.value = ""
	messages.value.push({ role: "user", text })
	messages.value.push({ role: "assistant", kind: "loading", stageText: "正在连接…" })
	busy.value = true
	scrollToBottom()

	const finish = (msg) => {
		messages.value[messages.value.length - 1] = msg
		busy.value = false
		controller = null
		scrollToBottom()
	}

	controller = chatStream({
		userInput: text,
		conversationId: conversationId.value,
		onStage: (s) => {
			// 必须通过 messages.value[...] 改，不能改上面那个普通对象：
			// ref 数组里的元素是响应式代理，改原对象不会触发重渲染
			lastMsg().stageText = s.text
			scrollToBottom()
		},
		onResult: (data) => {
			conversationId.value = data.conversation_id
			try { uni.setStorageSync(STORAGE_KEY, data.conversation_id) } catch (e) {}
			const res = data.result
			finish(roundToMessage(res.status, res, data.disclaimer))
		},
		onError: (e) => {
			finish({ role: "assistant", kind: "error", text: (e && e.message) || "网络错误，请检查后端是否启动" })
		}
	})
}

const stop = () => {
	if (controller) controller.abort()
	controller = null
	busy.value = false
	const m = lastMsg()
	if (m && m.kind === "loading") {
		// 后端检测到断开会取消 agent 任务，这一轮不会存库。
		// 所以上面那条用户消息刷新之后会消失，这是已知的不一致，
		// 但比留一个永远转圈的条目好
		messages.value[messages.value.length - 1] = {
			role: "assistant", kind: "error", text: "已停止，这一轮没有保存"
		}
	}
}

const newChat = () => {
	if (busy.value) stop()
	try { uni.removeStorageSync(STORAGE_KEY) } catch (e) {}
	conversationId.value = null
	messages.value = []
	opened.value = {}
}

const goBack = () => {
	// 从功能选择页 navigateTo 进来的，所以返回键能回去；
	// 万一栈被清了（比如刷新），就退回选择页而不是留在一个没有出口的页面上
	const pages = getCurrentPages()
	if (pages.length > 1) uni.navigateBack()
	else uni.reLaunch({ url: "/pages/select/select" })
}

onMounted(loadHistory)
onUnmounted(() => {
	// 离开页面一定要断开，否则后端那个 agent 任务会继续跑完、继续烧模型调用
	if (controller) controller.abort()
})
</script>

<style>
.page { display: flex; flex-direction: column; height: 100vh; background: #F5F6F8; }
.list { flex: 1; padding: 28rpx 26rpx 0; box-sizing: border-box; }
.pad { height: 24rpx; }

/* 空状态 */
.empty { padding: 70rpx 20rpx 30rpx; }
.empty-h { display: block; font-size: 38rpx; font-weight: 600; color: #16181C; }
.empty-p { display: block; margin-top: 16rpx; font-size: 26rpx; line-height: 42rpx; color: #9AA2AC; }
.chips { margin-top: 36rpx; display: flex; flex-direction: column; gap: 16rpx; }
.chip {
	background: #fff; border: 2rpx solid #E6E8EB; border-radius: 16rpx;
	padding: 24rpx 26rpx;
}
.chip:active { background: #F0F5F5; border-color: #B9D6D4; }
.chip-t { font-size: 26rpx; color: #40474F; }

/* 气泡 */
.row { display: flex; margin-bottom: 22rpx; }
.row-l { justify-content: flex-start; }
.row-r { justify-content: flex-end; }
.bub { max-width: 84%; padding: 22rpx 26rpx; font-size: 28rpx; line-height: 44rpx; }
.bub-u { background: #2E7D7B; color: #fff; border-radius: 22rpx 22rpx 6rpx 22rpx; }
.bub-a { background: #fff; color: #16181C; border: 2rpx solid #E6E8EB; border-radius: 22rpx 22rpx 22rpx 6rpx; }
.bub-err { background: #FDF3F0; border-color: #F0D6CC; }
.err-t { color: #A65A44; font-size: 26rpx; }
.ask { white-space: pre-wrap; color: #40474F; }

/* 等待中 */
.loading { display: flex; align-items: center; gap: 16rpx; }
.dots { display: flex; gap: 8rpx; }
.dot { width: 12rpx; height: 12rpx; border-radius: 50%; background: #2E7D7B; opacity: .35; animation: blink 1.2s infinite; }
.dot:nth-child(2) { animation-delay: .2s; }
.dot:nth-child(3) { animation-delay: .4s; }
@keyframes blink { 0%, 60%, 100% { opacity: .3; } 30% { opacity: 1; } }
.stage { color: #626A75; font-size: 25rpx; }

/* 名字卡片 */
.cards { width: 84%; padding: 8rpx 26rpx 20rpx; }
.ncard { padding: 24rpx 0; border-bottom: 2rpx solid #F0F1F3; }
.ncard:last-of-type { border-bottom: none; }
.nrow { display: flex; align-items: center; gap: 14rpx; }
.nname { font-size: 36rpx; font-weight: 600; color: #16181C; letter-spacing: 2rpx; }
.ntag { font-size: 20rpx; padding: 3rpx 12rpx; border-radius: 999rpx; background: #E7F2F1; color: #2E7D7B; }
.nmean { display: block; margin-top: 12rpx; font-size: 26rpx; line-height: 42rpx; color: #626A75; }
.nsrc { display: flex; align-items: stretch; margin-top: 14rpx; gap: 14rpx; }
.nsrc-bar { width: 4rpx; background: #D8DEE4; border-radius: 2rpx; flex-shrink: 0; }
.nsrc-t { flex: 1; font-size: 23rpx; line-height: 36rpx; color: #9AA2AC; }

/* 风险 */
.risk { margin-top: 16rpx; background: #FBFAF7; border: 2rpx solid #EFE9DC; border-radius: 14rpx; padding: 16rpx 20rpx; }
.risk-h { display: flex; align-items: center; gap: 10rpx; }
.risk-n { font-size: 24rpx; font-weight: 600; color: #A6762F; }
.risk-l { font-size: 24rpx; color: #A6762F; flex: 1; }
.risk-more { font-size: 22rpx; color: #B4BAC2; }
.risk-b { margin-top: 14rpx; }
.ritem { padding: 14rpx 0; border-top: 2rpx solid #EFE9DC; }
.rrow { display: flex; align-items: center; gap: 12rpx; }
.rclause { font-size: 24rpx; font-weight: 600; color: #40474F; flex: 1; }
.rgrade { font-size: 19rpx; padding: 2rpx 10rpx; border-radius: 6rpx; }
.g-ban { background: #FBE9E4; color: #A6503C; }
.g-ref { background: #FBF1DE; color: #9A7320; }
.g-exc { background: #E7F2F1; color: #2E7D7B; }
.rlaw { display: block; margin-top: 6rpx; font-size: 20rpx; color: #B4BAC2; }
.reason { display: flex; align-items: flex-start; gap: 10rpx; margin-top: 12rpx; }
.rtag { flex-shrink: 0; font-size: 19rpx; padding: 2rpx 10rpx; border-radius: 6rpx; margin-top: 4rpx; }
.rtag-rule { background: #E4F0EA; color: #3D7355; }
.rtag-ai { background: #E9ECF8; color: #5160A8; }
.rtext { flex: 1; font-size: 24rpx; line-height: 38rpx; color: #626A75; }

.disc { display: block; margin-top: 18rpx; padding-top: 16rpx; border-top: 2rpx solid #F0F1F3; font-size: 20rpx; line-height: 32rpx; color: #B4BAC2; }

/* 输入区 */
.bar { display: flex; align-items: center; gap: 16rpx; padding: 18rpx 26rpx; background: #fff; border-top: 2rpx solid #E6E8EB; }
.ipt { flex: 1; height: 80rpx; background: #F5F6F8; border: 2rpx solid #E6E8EB; border-radius: 999rpx; padding: 0 28rpx; font-size: 28rpx; color: #16181C; }
.ph { color: #B4BAC2; font-size: 26rpx; }
.sbtn { width: 76rpx; height: 76rpx; border-radius: 50%; background: #2E7D7B; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.sbtn-off { background: #D5D9DE; }
.sbtn-stop { background: #C4705C; }
.sbtn-t { color: #fff; font-size: 32rpx; line-height: 32rpx; }

.foot { display: flex; justify-content: space-between; padding: 14rpx 30rpx 22rpx; background: #fff; }
.foot-l, .foot-r { font-size: 23rpx; color: #9AA2AC; }
</style>
