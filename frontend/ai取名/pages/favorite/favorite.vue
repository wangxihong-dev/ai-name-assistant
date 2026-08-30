<template>
	<view class="page">
		<!-- 顶部 -->
		<view class="header anim-fade-up">
			<view class="header-badge">❤</view>
			<text class="title">我的收藏</text>
			<text class="subtitle">珍藏每一个心动的名字</text>
		</view>

		<!-- 加载骨架屏 -->
		<view v-if="loading" class="list">
			<view v-for="i in 3" :key="i" class="fav-card skeleton-card">
				<view class="skeleton sk-name"></view>
				<view class="skeleton sk-line"></view>
				<view class="skeleton sk-line short"></view>
			</view>
		</view>

		<!-- 空状态 -->
		<view v-else-if="favorites.length === 0" class="empty-box anim-fade-up">
			<view class="empty-heart">💝</view>
			<text class="empty-title">还没有收藏的名字</text>
			<text class="empty-desc">遇见心动的名字，点亮小爱心吧</text>
			<button class="empty-btn" @click="goName">✨ 去取名</button>
		</view>

		<!-- 收藏列表 -->
		<view v-else class="list">
			<view
				v-for="(item, index) in favorites"
				:key="item.id"
				class="fav-card anim-fade-up"
				:style="{ animationDelay: (index * 60) + 'ms' }"
			>
				<view class="fav-top">
					<view class="fav-info">
						<text class="fav-name">{{ item.name }}</text>
						<text class="fav-time">🕐 {{ formatTime(item.created_at) }}</text>
					</view>
					<button class="remove-btn" :disabled="removingId === item.id" @click.stop="removeFavorite(item)">
						{{ removingId === item.id ? '移除中' : '移除' }}
					</button>
				</view>

				<view class="fav-section">
					<text class="fav-label">📖 出处</text>
					<text class="fav-content">{{ item.reference }}</text>
				</view>

				<view class="fav-section">
					<text class="fav-label">🌱 寓意</text>
					<text class="fav-content">{{ item.moral }}</text>
				</view>
			</view>
		</view>
	</view>
</template>

<script setup>
import { ref } from "vue"
import { onShow } from "@dcloudio/uni-app"
import API from "../../common/api.js"

const favorites = ref([])
const loading = ref(true)
const removingId = ref(null)

// 每次进入页面都刷新，保证数据最新
onShow(() => {
	loadFavorites()
})

const loadFavorites = async () => {
	loading.value = true
	try {
		const data = await API.getFavorites()
		favorites.value = data.favorites || []
	} catch (e) {
		uni.showToast({ title: e.message || "获取收藏失败", icon: "none" })
	} finally {
		loading.value = false
	}
}

// 取消收藏：先确认，再删除，再本地移除（少一次请求，更流畅）
const removeFavorite = (item) => {
	uni.showModal({
		title: "取消收藏",
		content: `确定移除「${item.name}」吗？`,
		confirmText: "移除",
		confirmColor: "#C58B4B",
		success: async (res) => {
			if (!res.confirm) return
			removingId.value = item.id
			try {
				await API.removeFavorite(item.id)
				favorites.value = favorites.value.filter((f) => f.id !== item.id)
				uni.showToast({ title: "已移除", icon: "none" })
			} catch (e) {
				uni.showToast({ title: e.message || "移除失败", icon: "none" })
			} finally {
				removingId.value = null
			}
		}
	})
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
	margin-bottom: 48rpx;
}

.header-badge {
	width: 96rpx;
	height: 96rpx;
	margin: 0 auto 20rpx;
	border-radius: 50%;
	background: linear-gradient(135deg, #E8A98B, #D98C7A);
	color: #fff;
	font-size: 48rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	box-shadow: 0 12rpx 30rpx rgba(217, 140, 122, 0.35);
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

/* 列表 */
.list {
	display: flex;
	flex-direction: column;
	gap: 28rpx;
}

.fav-card {
	background: rgba(255, 255, 255, 0.92);
	border-radius: 32rpx;
	padding: 36rpx;
	box-shadow: 0 14rpx 36rpx rgba(154, 107, 60, 0.10);
	border: 2rpx solid rgba(232, 185, 107, 0.16);
}

.fav-top {
	display: flex;
	justify-content: space-between;
	align-items: flex-start;
	gap: 20rpx;
}

.fav-info {
	display: flex;
	flex-direction: column;
	gap: 10rpx;
}

.fav-name {
	font-size: 52rpx;
	font-weight: bold;
	background: linear-gradient(135deg, #C58B4B, #9B6B3C);
	-webkit-background-clip: text;
	background-clip: text;
	color: transparent;
	line-height: 1.2;
}

.fav-time {
	font-size: 22rpx;
	color: #B9A48E;
}

.remove-btn {
	flex-shrink: 0;
	margin: 0;
	padding: 0 30rpx;
	height: 60rpx;
	line-height: 60rpx;
	font-size: 24rpx;
	color: #C58B4B;
	background: #FBF0DE;
	border-radius: 999rpx;
}

.remove-btn[disabled] {
	opacity: 0.6;
}

.fav-section {
	margin-top: 26rpx;
	background: #FFF9F0;
	border-radius: 20rpx;
	padding: 24rpx 26rpx;
}

.fav-label {
	display: block;
	font-size: 24rpx;
	font-weight: bold;
	color: #C58B4B;
}

.fav-content {
	display: block;
	margin-top: 10rpx;
	font-size: 27rpx;
	color: #6B5843;
	line-height: 42rpx;
}

/* 骨架屏 */
.skeleton-card {
	display: flex;
	flex-direction: column;
	gap: 22rpx;
}

.sk-name {
	height: 52rpx;
	width: 40%;
}

.sk-line {
	height: 30rpx;
	width: 100%;
}

.sk-line.short {
	width: 66%;
}

/* 空状态 */
.empty-box {
	text-align: center;
	padding: 140rpx 40rpx;
}

.empty-heart {
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
</style>


