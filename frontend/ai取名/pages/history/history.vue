<template>
	<view class="page">
		<!-- 顶部 -->
		<view class="header">
			<text class="title">📜 取名历史</text>
			<text class="subtitle">每一次取名，都是一份美好的期待</text>
		</view>

		<!-- 加载中 -->
		<view v-if="loading" class="loading-box">
			<text class="loading-text">正在回忆你的取名记录...</text>
		</view>

		<!-- 空状态 -->
		<view v-else-if="histories.length === 0" class="empty-box">
			<text class="empty-emoji">🌸</text>
			<text class="empty-title">还没有取名记录</text>
			<text class="empty-desc">快去为宝宝取一个好听的名字吧~</text>
			<button class="empty-btn" @click="goName">去取名</button>
		</view>

		<!-- 历史记录列表 -->
		<view v-else class="history-list">
			<view
				v-for="(item, index) in histories"
				:key="item.id"
				class="history-card"
				@click="toggleExpand(index)"
			>
				<!-- 卡片头部 -->
				<view class="card-header">
					<view class="header-left">
						<text class="surname">{{ item.surname }}姓</text>
						<text class="tag" :class="item.gender === '男' ? 'boy' : 'girl'">
							{{ item.gender === '男' ? '👦 男孩' : item.gender === '女' ? '👧 女孩' : '🎈 不限' }}
						</text>
						<text class="tag length">{{ item.length }}</text>
					</view>
					<text class="arrow" :class="{ expanded: expandedIndex === index }">▼</text>
				</view>

				<!-- 其他要求 -->
				<view v-if="item.other" class="other-row">
					<text class="other-label">💭 寄语：</text>
					<text class="other-content">{{ item.other }}</text>
				</view>

				<!-- 时间 -->
				<text class="time">🕐 {{ formatTime(item.created_at) }}</text>

				<!-- 展开的名字详情 -->
				<view v-if="expandedIndex === index" class="names-detail">
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
import { ref, onMounted } from "vue"

const histories = ref([])
const loading = ref(true)
const expandedIndex = ref(-1)

// 页面加载时获取历史记录
onMounted(() => {
	getHistory()
})

// 获取历史记录
const getHistory = () => {
	const token = uni.getStorageSync("token")

	uni.request({
		url: "http://127.0.0.1:8000/name/history",
		method: "GET",
		header: {
			Authorization: "Bearer " + token
		},
		success(res) {
			if (res.data && res.data.histories) {
				histories.value = res.data.histories
			}
		},
		fail() {
			uni.showToast({
				title: "获取历史记录失败",
				icon: "none"
			})
		},
		complete() {
			loading.value = false
		}
	})
}

// 展开/收起
const toggleExpand = (index) => {
	if (expandedIndex.value === index) {
		expandedIndex.value = -1
	} else {
		expandedIndex.value = index
	}
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

// 去取名页
const goName = () => {
	uni.reLaunch({
		url: "/pages/name/name"
	})
}
</script>

<style>
.page {
	min-height: 100vh;
	background: #fff7eb;
	padding: 40rpx 30rpx;
}

.header {
	text-align: center;
	margin-bottom: 40rpx;
}

.title {
	display: block;
	font-size: 48rpx;
	font-weight: bold;
	color: #946638;
}

.subtitle {
	display: block;
	font-size: 28rpx;
	color: #b88655;
	margin-top: 15rpx;
}

/* 加载中 */
.loading-box {
	text-align: center;
	padding: 100rpx 0;
}

.loading-text {
	color: #b88655;
	font-size: 30rpx;
}

/* 空状态 */
.empty-box {
	text-align: center;
	padding: 120rpx 40rpx;
}

.empty-emoji {
	display: block;
	font-size: 120rpx;
}

.empty-title {
	display: block;
	font-size: 36rpx;
	color: #946638;
	margin-top: 30rpx;
	font-weight: bold;
}

.empty-desc {
	display: block;
	font-size: 28rpx;
	color: #b88655;
	margin-top: 20rpx;
}

.empty-btn {
	margin-top: 50rpx;
	background: #c58b4b;
	color: white;
	border-radius: 50rpx;
	width: 300rpx;
}

/* 历史记录列表 */
.history-list {
	display: flex;
	flex-direction: column;
	gap: 25rpx;
}

.history-card {
	background: white;
	border-radius: 30rpx;
	padding: 35rpx;
	box-shadow: 0 8rpx 25rpx rgba(150, 100, 50, 0.1);
}

.card-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
}

.header-left {
	display: flex;
	align-items: center;
	gap: 15rpx;
	flex-wrap: wrap;
}

.surname {
	font-size: 36rpx;
	font-weight: bold;
	color: #946638;
}

.tag {
	font-size: 24rpx;
	padding: 6rpx 18rpx;
	border-radius: 20rpx;
}

.tag.boy {
	background: #e3f2fd;
	color: #1976d2;
}

.tag.girl {
	background: #fce4ec;
	color: #c2185b;
}

.tag.length {
	background: #fff3e0;
	color: #e65100;
}

.arrow {
	font-size: 24rpx;
	color: #c58b4b;
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
	font-size: 26rpx;
	color: #946638;
	flex-shrink: 0;
}

.other-content {
	font-size: 26rpx;
	color: #666;
	flex: 1;
	line-height: 40rpx;
}

.time {
	display: block;
	font-size: 24rpx;
	color: #999;
	margin-top: 15rpx;
}

/* 展开的名字详情 */
.names-detail {
	margin-top: 10rpx;
}

.divider {
	height: 2rpx;
	background: #f0e6d6;
	margin: 25rpx 0;
}

.detail-title {
	display: block;
	font-size: 30rpx;
	color: #946638;
	font-weight: bold;
	margin-bottom: 20rpx;
}

.name-item {
	background: #fffaf3;
	border-radius: 20rpx;
	padding: 25rpx;
	margin-bottom: 20rpx;
}

.name-item:last-child {
	margin-bottom: 0;
}

.name-text {
	display: block;
	text-align: center;
	font-size: 48rpx;
	font-weight: bold;
	color: #c58b4b;
	margin-bottom: 15rpx;
}

.name-info {
	margin-top: 12rpx;
}

.info-label {
	display: block;
	font-size: 24rpx;
	color: #946638;
	font-weight: bold;
}

.info-content {
	display: block;
	font-size: 26rpx;
	color: #666;
	line-height: 40rpx;
	margin-top: 8rpx;
}
</style>
