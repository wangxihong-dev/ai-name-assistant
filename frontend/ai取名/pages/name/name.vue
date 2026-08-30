<template>
	<view class="page">
		<!-- 顶部品牌区 -->
		<view class="hero anim-fade-up">
			<view class="header-top">
				<view class="brand">
					<text class="logo">✨ 鸿运取名</text>
					<text class="subtitle">AI 国学智能命名助手</text>
				</view>
				<view class="actions">
					<view class="action-chip" @click="goHistory">
						<text>📜</text><text>历史</text>
					</view>
					<view class="action-chip" @click="goFavorite">
						<text>❤</text><text>收藏</text>
					</view>
				</view>
			</view>
			<text class="desc">结合诗经、楚辞、唐诗宋词，为宝宝寻找寓意美好的名字</text>
		</view>

		<!-- 输入卡片 -->
		<view class="card anim-fade-up" :style="{ animationDelay: '70ms' }">
			<view class="field">
				<text class="label">宝宝姓氏</text>
				<view class="input-wrap">
					<input v-model="form.surname" class="input" maxlength="2" placeholder="例如：李" placeholder-class="ph" />
				</view>
			</view>

			<view class="field">
				<text class="label">宝宝性别</text>
				<view class="chip-row">
					<view
						v-for="g in genderOptions"
						:key="g.value"
						class="chip"
						:class="{ active: form.gender === g.value }"
						@click="form.gender = g.value"
					>{{ g.label }}</view>
				</view>
			</view>

			<view class="field">
				<text class="label">名字长度</text>
				<view class="chip-row">
					<view
						v-for="l in lengthOptions"
						:key="l.value"
						class="chip"
						:class="{ active: form.length === l.value }"
						@click="form.length = l.value"
					>{{ l.label }}</view>
				</view>
			</view>

			<view class="field">
				<text class="label">父母寄语</text>
				<view class="textarea-wrap">
					<textarea
						v-model="form.other"
						class="textarea"
						placeholder="例如：希望孩子温柔、有智慧、平安快乐"
						placeholder-class="ph"
					/>
				</view>
			</view>

			<button class="generate" :disabled="loading" @click="generate">
				<view v-if="loading" class="spinner light"></view>
				<text>{{ loading ? 'AI 正在取名...' : '✨ 开始取名' }}</text>
			</button>
		</view>

		<!-- 等待动画（分阶段提示，优化等待体验） -->
		<view v-if="loading" class="loading-box anim-fade-in">
			<view class="loading-orb">
				<view class="ring"></view>
				<text class="orb-core">✨</text>
			</view>
			<text class="loading-title">{{ stageText }}</text>
			<view class="dots">
				<view v-for="i in 4" :key="i" class="dot" :class="{ on: stageIndex >= i - 1 }"></view>
			</view>
			<text class="loading-desc">正在为你翻阅典籍、检索诗句、推敲音韵</text>
		</view>

		<!-- 结果区域 -->
		<view v-if="!loading && result" class="result">
			<view v-if="result.message" class="save-warn anim-fade-in">
				<text>💡 {{ result.message }}</text>
			</view>
			<view v-else class="save-tip anim-fade-in">
				<text>✨ 已为你保存这次取名记录，可在历史中查看</text>
			</view>

			<text class="result-title">🎉 AI 推荐名字</text>

			<view
				v-for="(item, index) in result.names"
				:key="item.name"
				class="name-card anim-fade-up"
				:style="{ animationDelay: (index * 110) + 'ms' }"
			>
				<text class="name">{{ item.name }}</text>

				<view class="line"></view>

				<view class="info-block">
					<text class="info">📖 出处</text>
					<text class="content">{{ item.reference }}</text>
				</view>

				<view class="info-block">
					<text class="info">🌱 寓意</text>
					<text class="content">{{ item.moral }}</text>
				</view>

				<button
					class="save"
					:class="{ saved: isFavorited(item.name) }"
					:disabled="favoritingName === item.name || isFavorited(item.name)"
					@click="favorite(item)"
				>
					{{ isFavorited(item.name) ? '♥ 已收藏' : '♡ 收藏名字' }}
				</button>
			</view>
		</view>
	</view>
</template>

<script setup>
import { ref, reactive, onUnmounted } from "vue"
import API from "../../common/api.js"

const genderOptions = [
	{ label: "👦 男孩", value: "男" },
	{ label: "👧 女孩", value: "女" }
]

const lengthOptions = [
	{ label: "单字名", value: "两字" },
	{ label: "双字名", value: "三字" }
]

const form = ref({
	surname: "",
	gender: "",
	length: "三字",
	other: "",
	exclude: []
})

const loading = ref(false)
const result = ref(null)
const favoritedNames = reactive({})   // 已收藏名字（本页内状态，避免重复收藏）
const favoritingName = ref(null)      // 正在收藏的名字，防重复点击

// 等待动画：分阶段文案 + 定时器
const stages = [
	"正在翻阅经典典籍…",
	"正在检索美好诗句…",
	"正在斟酌音律韵脚…",
	"正在精雕细琢名字…"
]
const stageIndex = ref(0)
const stageText = ref(stages[0])
let stageTimer = null

const startStage = () => {
	stageIndex.value = 0
	stageText.value = stages[0]
	stageTimer = setInterval(() => {
		stageIndex.value = (stageIndex.value + 1) % stages.length
		stageText.value = stages[stageIndex.value]
	}, 2200)
}

const stopStage = () => {
	if (stageTimer) {
		clearInterval(stageTimer)
		stageTimer = null
	}
}

// 生成名字
const generate = async () => {
	if (!form.value.surname) {
		uni.showToast({ title: "请输入宝宝姓氏", icon: "none" })
		return
	}
	if (!form.value.gender) {
		uni.showToast({ title: "请选择宝宝性别", icon: "none" })
		return
	}

	const token = uni.getStorageSync("token")
	if (!token) {
		uni.showToast({ title: "请先登录", icon: "none" })
		setTimeout(() => uni.reLaunch({ url: "/pages/index/index" }), 900)
		return
	}

	if (loading.value) return // 防重复提交

	loading.value = true
	result.value = null
	startStage()

	try {
		const data = await API.generateName(form.value)
		result.value = data
	} catch (e) {
		uni.showToast({ title: e.message || "生成失败", icon: "none" })
	} finally {
		loading.value = false
		stopStage()
	}
}

// 收藏名字
const favorite = async (item) => {
	if (favoritingName.value) return
	favoritingName.value = item.name
	try {
		await API.addFavorite({
			name: item.name,
			reference: item.reference,
			moral: item.moral
		})
		favoritedNames[item.name] = true
		uni.showToast({ title: "已收藏 ♥", icon: "none" })
	} catch (e) {
		uni.showToast({ title: e.message || "收藏失败", icon: "none" })
	} finally {
		favoritingName.value = null
	}
}

const isFavorited = (name) => !!favoritedNames[name]

const goHistory = () => {
	uni.navigateTo({ url: "/pages/history/history" })
}

const goFavorite = () => {
	uni.navigateTo({ url: "/pages/favorite/favorite" })
}

onUnmounted(() => {
	stopStage()
})
</script>

<style>
.page {
	min-height: 100vh;
	background: linear-gradient(180deg, #FFF4E0 0%, #FAF4EA 500rpx);
	padding: 50rpx 32rpx 90rpx;
}

/* 顶部 */
.hero {
	margin-bottom: 40rpx;
}

.header-top {
	display: flex;
	justify-content: space-between;
	align-items: flex-start;
}

.brand {
	display: flex;
	flex-direction: column;
}

.logo {
	font-size: 48rpx;
	font-weight: bold;
	background: linear-gradient(135deg, #9B6B3C, #C58B4B);
	-webkit-background-clip: text;
	background-clip: text;
	color: transparent;
}

.subtitle {
	font-size: 24rpx;
	color: #8C735C;
	margin-top: 10rpx;
}

.actions {
	display: flex;
	gap: 16rpx;
}

.action-chip {
	display: flex;
	align-items: center;
	gap: 8rpx;
	padding: 14rpx 24rpx;
	background: rgba(255, 255, 255, 0.85);
	border-radius: 999rpx;
	font-size: 24rpx;
	color: #8C735C;
	box-shadow: 0 8rpx 20rpx rgba(154, 107, 60, 0.10);
	border: 2rpx solid rgba(232, 185, 107, 0.22);
}

.desc {
	display: block;
	margin-top: 26rpx;
	font-size: 26rpx;
	color: #B9A48E;
	line-height: 42rpx;
}

/* 表单卡片 */
.card {
	background: rgba(255, 255, 255, 0.94);
	border-radius: 40rpx;
	padding: 44rpx 36rpx;
	box-shadow: 0 18rpx 50rpx rgba(154, 107, 60, 0.13);
	border: 2rpx solid rgba(232, 185, 107, 0.18);
}

.field {
	margin-bottom: 36rpx;
}

.label {
	display: block;
	color: #8C735C;
	margin-bottom: 16rpx;
	font-size: 27rpx;
	font-weight: bold;
}

.input-wrap {
	display: flex;
	align-items: center;
	height: 94rpx;
	background: #FFF9F0;
	border-radius: 24rpx;
	padding: 0 28rpx;
	border: 2rpx solid #F0E6D6;
}

.input {
	flex: 1;
	height: 94rpx;
	font-size: 30rpx;
	color: #4A3728;
}

.ph {
	color: #C9BBA4;
}

.chip-row {
	display: flex;
	gap: 20rpx;
}

.chip {
	flex: 1;
	text-align: center;
	height: 88rpx;
	line-height: 88rpx;
	background: #FFF9F0;
	border-radius: 24rpx;
	color: #8C735C;
	font-size: 28rpx;
	border: 2rpx solid #F0E6D6;
	transition: all 0.25s;
}

.chip.active {
	background: linear-gradient(135deg, #E8B96B, #C58B4B);
	color: #fff;
	border-color: transparent;
	box-shadow: 0 10rpx 22rpx rgba(197, 139, 75, 0.32);
}

.textarea-wrap {
	background: #FFF9F0;
	border-radius: 24rpx;
	padding: 24rpx 28rpx;
	border: 2rpx solid #F0E6D6;
}

.textarea {
	width: 100%;
	height: 160rpx;
	font-size: 29rpx;
	color: #4A3728;
	line-height: 44rpx;
}

.generate {
	margin-top: 12rpx;
	height: 102rpx;
	line-height: 102rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	gap: 16rpx;
	background: linear-gradient(135deg, #E8B96B, #C58B4B);
	color: #fff;
	font-size: 33rpx;
	font-weight: bold;
	border-radius: 999rpx;
	box-shadow: 0 16rpx 34rpx rgba(197, 139, 75, 0.38);
}

.generate[disabled] {
	opacity: 0.75;
}

.spinner {
	width: 32rpx;
	height: 32rpx;
	border: 4rpx solid rgba(255, 255, 255, 0.4);
	border-top-color: #fff;
	border-radius: 50%;
	animation: spin 0.8s linear infinite;
}

/* 等待动画 */
.loading-box {
	margin-top: 40rpx;
	background: rgba(255, 255, 255, 0.9);
	border-radius: 40rpx;
	padding: 64rpx 40rpx;
	text-align: center;
	box-shadow: 0 18rpx 50rpx rgba(154, 107, 60, 0.12);
}

.loading-orb {
	position: relative;
	width: 130rpx;
	height: 130rpx;
	margin: 0 auto 34rpx;
}

.ring {
	position: absolute;
	inset: 0;
	border: 4rpx dashed rgba(197, 139, 75, 0.5);
	border-radius: 50%;
	animation: spin 3.2s linear infinite;
}

.orb-core {
	position: absolute;
	inset: 22rpx;
	border-radius: 50%;
	background: linear-gradient(135deg, #E8B96B, #C58B4B);
	display: flex;
	align-items: center;
	justify-content: center;
	font-size: 40rpx;
	animation: pulse 1.8s ease-in-out infinite;
}

.loading-title {
	display: block;
	font-size: 34rpx;
	font-weight: bold;
	color: #4A3728;
}

.dots {
	display: flex;
	justify-content: center;
	gap: 14rpx;
	margin-top: 30rpx;
}

.dot {
	width: 16rpx;
	height: 16rpx;
	border-radius: 50%;
	background: #F0E6D6;
	transition: all 0.35s;
}

.dot.on {
	background: #C58B4B;
	transform: scale(1.25);
}

.loading-desc {
	display: block;
	margin-top: 30rpx;
	color: #B9A48E;
	font-size: 24rpx;
}

/* 结果 */
.result {
	margin-top: 46rpx;
}

.save-tip,
.save-warn {
	border-radius: 20rpx;
	padding: 22rpx 28rpx;
	margin-bottom: 30rpx;
	text-align: center;
	font-size: 25rpx;
}

.save-tip {
	background: rgba(232, 185, 107, 0.16);
	color: #9B6B3C;
}

.save-warn {
	background: #FFF3E0;
	color: #C77F36;
}

.result-title {
	display: block;
	font-size: 40rpx;
	font-weight: bold;
	color: #4A3728;
	margin-bottom: 28rpx;
}

.name-card {
	background: rgba(255, 255, 255, 0.94);
	padding: 44rpx 38rpx;
	border-radius: 36rpx;
	margin-bottom: 28rpx;
	box-shadow: 0 14rpx 38rpx rgba(154, 107, 60, 0.12);
	border: 2rpx solid rgba(232, 185, 107, 0.18);
}

.name {
	display: block;
	text-align: center;
	font-size: 72rpx;
	font-weight: bold;
	background: linear-gradient(135deg, #C58B4B, #9B6B3C);
	-webkit-background-clip: text;
	background-clip: text;
	color: transparent;
}

.line {
	height: 2rpx;
	background: #F0E6D6;
	margin: 30rpx 0;
}

.info-block {
	margin-top: 22rpx;
}

.info {
	display: block;
	color: #C58B4B;
	font-size: 26rpx;
	font-weight: bold;
}

.content {
	display: block;
	color: #6B5843;
	line-height: 44rpx;
	margin-top: 12rpx;
	font-size: 28rpx;
}

.save {
	margin-top: 34rpx;
	height: 84rpx;
	line-height: 84rpx;
	background: #FBF0DE;
	color: #C58B4B;
	border-radius: 999rpx;
	font-size: 28rpx;
	border: 2rpx solid rgba(232, 185, 107, 0.35);
	transition: all 0.25s;
}

.save.saved {
	background: linear-gradient(135deg, #E8A98B, #D98C7A);
	color: #fff;
	border-color: transparent;
}

.save[disabled] {
	opacity: 0.7;
}
</style>
