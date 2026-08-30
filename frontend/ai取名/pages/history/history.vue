<template>
	<view class="page">
		<!-- 顶部 -->
		<view class="header anim-fade-up">
			<text class="title">📜 取名历史</text>
			<text class="subtitle">每一次取名，都是一份美好的期待</text>
		</view>

		<!-- 加载骨架屏 -->
		<view v-if="loading" class="history-list">
			<view v-for="i in 3" :key="i" class="history-card skeleton-card">
				<view class="skeleton sk-head"></view>
				<view class="skeleton sk-line"></view>
				<view class="skeleton sk-line short"></view>
			</view>
		</view>

		<!-- 空状态 -->
		<view v-else-if="histories.length === 0" class="empty-box anim-fade-up">
			<text class="empty-emoji">🌸</text>
			<text class="empty-title">还没有取名记录</text>
			<text class="empty-desc">快去为宝宝取一个好听的名字吧~</text>
			<button class="empty-btn" @click="goName">✨ 去取名</button>
		</view>

		<!-- 历史记录列表 -->
		<view v-else class="history-list">
			<view
				v-for="(item, index) in histories"
				:key="item.id"
				class="history-card anim-fade-up"
				:style="{ animationDelay: (index * 60) + 'ms' }"
				@click="toggleExpand(index)"
			>
				<!-- 卡片头部 -->
				<view class="card-header">
					<view class="header-left">
						<text class="surname">{{ item.surname }}姓</text>
						<text class="tag" :class="item.gender === '男' ? 'boy' : item.gender === '女' ? 'girl' : 'all'">
							{{ item.gender === '男' ? '👦 男孩' : item.gender === '女' ? '👧 女孩' : '🎈 不限' }}
						</text>
						<text class="tag length">{{ item.length }}</text>
					</view>
					<text class="arrow" :class="{ expanded: expandedIndex === index }">▾</text>
				</view>

				<!-- 寄语 -->
				<view v-if="item.other" class="other-row">
					<text class="other-label">💭 寄语：</text>
					<text class="other-content">{{ item.other }}</text>
				</view>

				<!-- 时间 -->
				<text class="time">🕐 {{ formatTime(item.created_at) }}</text>

				<!-- 展开的名字详情 -->
				<view v-if="expandedIndex === index" class="names-detail anim-fade-in">
					<view class="divider"></view>
					<text class="detail-title">✨ AI 推荐的名字</text>
					<view
						v-for="(name, nameIndex) in item.result.names"
						:key="nameIndex"
						class="name-item"
					>
						<text class="name-text">{{ name.name }}</text>
						<view class="name-info">
							<text class="info-label">📖 出处</text>
							<text class="info-content">{{ name.reference }}</text>
						</view>
						<view class="name-info">
							<text class="info-label">🌱 寓意</text>
							<text class="info-content">{{ name.moral }}</text>
						</view>
					</view>
				</view>
			</view>
		</view>
	</view>
</template>

<script setup>
import { ref } from "vue"
import { onShow } from "@dcloudio/uni-app"
import API from "../../common/api.js"

const histories = ref([])
const loading = ref(true)
const expandedIndex = ref(-1)

// 每次进入页面都刷新（从取名页返回后能看到最新记录）
onShow(() => {
	getHistory()
})

const getHistory = async () => {
	loading.value = true
	try {
		const data = await API.getHistory()
		histories.value = data.histories || []
	} catch (e) {
		uni.showToast({ title: e.message || "获取历史记录失败", icon: "none" })
	} finally {
		loading.value = false
	}
}

// 展开/收起
const toggleExpand = (index) => {
	expandedIndex.value = expandedIndex.value === index ? -1 : index
}

// 格式化时间
const formatTime = (timeStr) => {
	if (!timeStr) return ""
	const date = new Date(timeStr)
	const year = date.getFullYear()
	const month = String(date.getMonth() + 1).padStart(2, "0")
	const day = String(date.getDate()).padStart(2, "0")
	const hour = String(date.getHours()).padStart(2, "0")
	const minute = String(date.getMinutes()).padStart(2, "0")
	return `${year}-${month}-${day} ${hour}:${minute}`
}

const goName = () => {
	uni.reLaunch({ url: "/pages/name/name" })
}
</script>

<style>
.page {
	min-height: 100vh;
	background: linear-gradient(180deg, #FFF4E0 0%, #FAF4EA 420rpx);
	padding: 40rpx 30rpx 80rpx;
}

.header {
	text-align: center;
	margin-bottom: 44rpx;
}

.title {
	display: block;
	font-size: 48rpx;
	font-weight: bold;
	color: #4A3728;
}

.subtitle {
	display: block;
	font-size: 26rpx;
	color: #B9A48E;
	margin-top: 14rpx;
}

/* 骨架屏 */
.skeleton-card {
	display: flex;
	flex-direction: column;
	gap: 20rpx;
}

.sk-head {
	height: 44rpx;
	width: 46%;
}

.sk-line {
	height: 28rpx;
	width: 100%;
}

.sk-line.short {
	width: 60%;
}

/* 空状态 */
.empty-box {
	text-align: center;
	padding: 140rpx 40rpx;
}

.empty-emoji {
	display: block;
	font-size: 110rpx;
	margin-bottom: 30rpx;
	animation: float 3s ease-in-out infinite;
}

.empty-title {
	display: block;
	font-size: 36rpx;
	font-weight: bold;
	color: #4A3728;
}

.empty-desc {
	display: block;
	font-size: 27rpx;
	color: #B9A48E;
	margin-top: 18rpx;
}

.empty-btn {
	margin-top: 56rpx;
	width: 320rpx;
	background: linear-gradient(135deg, #E8B96B, #C58B4B);
	color: #fff;
	border-radius: 999rpx;
	box-shadow: 0 14rpx 30rpx rgba(197, 139, 75, 0.35);
}

/* 列表 */
.history-list {
	display: flex;
	flex-direction: column;
	gap: 26rpx;
}

.history-card {
	background: rgba(255, 255, 255, 0.94);
	border-radius: 32rpx;
	padding: 36rpx;
	box-shadow: 0 12rpx 32rpx rgba(154, 107, 60, 0.10);
	border: 2rpx solid rgba(232, 185, 107, 0.16);
}

.card-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
}

.header-left {
	display: flex;
	align-items: center;
	gap: 14rpx;
	flex-wrap: wrap;
}

.surname {
	font-size: 36rpx;
	font-weight: bold;
	color: #4A3728;
}

.tag {
	font-size: 23rpx;
	padding: 8rpx 20rpx;
	border-radius: 999rpx;
}

.tag.boy {
	background: #EAF3FB;
	color: #5A86B8;
}

.tag.girl {
	background: #FBEAEE;
	color: #C57F91;
}

.tag.all {
	background: #F6E3C8;
	color: #9B6B3C;
}

.tag.length {
	background: #FFF3E0;
	color: #C77F36;
}

.arrow {
	font-size: 26rpx;
	color: #C58B4B;
	transition: transform 0.3s;
}

.arrow.expanded {
	transform: rotate(180deg);
}

.other-row {
	margin-top: 20rpx;
	display: flex;
	align-items: flex-start;
}

.other-label {
	font-size: 25rpx;
	color: #8C735C;
	flex-shrink: 0;
	font-weight: bold;
}

.other-content {
	font-size: 25rpx;
	color: #6B5843;
	flex: 1;
	line-height: 40rpx;
}

.time {
	display: block;
	font-size: 22rpx;
	color: #B9A48E;
	margin-top: 16rpx;
}

/* 展开详情 */
.names-detail {
	margin-top: 10rpx;
}

.divider {
	height: 2rpx;
	background: #F0E6D6;
	margin: 26rpx 0;
}

.detail-title {
	display: block;
	font-size: 29rpx;
	color: #8C735C;
	font-weight: bold;
	margin-bottom: 20rpx;
}

.name-item {
	background: #FFF9F0;
	border-radius: 22rpx;
	padding: 28rpx;
	margin-bottom: 18rpx;
	border: 2rpx solid #F6EDDE;
}

.name-item:last-child {
	margin-bottom: 0;
}

.name-text {
	display: block;
	text-align: center;
	font-size: 46rpx;
	font-weight: bold;
	background: linear-gradient(135deg, #C58B4B, #9B6B3C);
	-webkit-background-clip: text;
	background-clip: text;
	color: transparent;
	margin-bottom: 14rpx;
}

.name-info {
	margin-top: 12rpx;
}

.info-label {
	display: block;
	font-size: 23rpx;
	color: #C58B4B;
	font-weight: bold;
}

.info-content {
	display: block;
	font-size: 25rpx;
	color: #6B5843;
	line-height: 40rpx;
	margin-top: 8rpx;
}
</style>


