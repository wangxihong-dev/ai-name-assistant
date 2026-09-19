<template>
	<view class="page">
		<view class="wrap">
			<view class="head">
				<text class="h1">选一个开始</text>
				<text class="h2">两个功能互相独立，进去之后配色会跟着换</text>
			</view>

			<!-- 宝宝取名：暖色，表单版 -->
			<view class="card" @click="go('/pages/name/name')">
				<view class="bar bar-warm"></view>
				<view class="body">
					<view class="row1">
						<text class="name">宝宝取名</text>
						<text class="tag tag-warm">表单版</text>
					</view>
					<text class="desc">诗经、楚辞、唐诗宋词，配合姓氏、性别、字数和音律，一次填完直接出五个名字</text>
					<text class="go go-warm">开始 →</text>
				</view>
			</view>

			<!-- 品牌取名：冷色，对话版 -->
			<view class="card" @click="go('/pages/chat/chat')">
				<view class="bar bar-cool"></view>
				<view class="body">
					<view class="row1">
						<text class="name">品牌／产品取名</text>
						<text class="tag tag-cool">对话版</text>
					</view>
					<text class="desc">边聊边定。每个名字都会过一遍商标法禁用字样，风险带条款号和出处，还能拿用户自己的名字来查</text>
					<text class="go go-cool">开始 →</text>
				</view>
			</view>

			<view class="foot">
				<text class="foot-link" @click="goBlog">技术博客：这个项目是怎么做的</text>
			</view>
		</view>
	</view>
</template>

<script setup>
// 用 navigateTo 不用 reLaunch：这样两个子页面的导航栏返回键能回到这里
const go = (url) => { uni.navigateTo({ url }) }

// 博客是 VitePress 静态站，挂在 /blog/，不在 uni-app 路由里
const goBlog = () => {
	// #ifdef H5
	window.location.href = "/blog/"
	// #endif
	// #ifndef H5
	uni.showToast({ title: "请在浏览器里访问 /blog/", icon: "none" })
	// #endif
}
</script>

<style>
.page { min-height: 100vh; background: #F5F6F8; }
.wrap { max-width: 760rpx; margin: 0 auto; padding: 90rpx 36rpx 60rpx; }

.head { margin-bottom: 48rpx; }
.h1 { display: block; font-size: 46rpx; font-weight: 600; color: #16181C; letter-spacing: 1rpx; }
.h2 { display: block; margin-top: 14rpx; font-size: 25rpx; color: #9AA2AC; }

.card {
	display: flex; background: #fff; border: 2rpx solid #E6E8EB;
	border-radius: 24rpx; margin-bottom: 26rpx; overflow: hidden;
	transition: transform .15s, box-shadow .15s;
}
.card:active { transform: scale(.99); }
.bar { width: 8rpx; flex-shrink: 0; }
.bar-warm { background: #C58B4B; }
.bar-cool { background: #2E7D7B; }

.body { flex: 1; padding: 36rpx 34rpx; }
.row1 { display: flex; align-items: center; gap: 16rpx; }
.name { font-size: 34rpx; font-weight: 600; color: #16181C; }
.tag { font-size: 20rpx; padding: 4rpx 14rpx; border-radius: 999rpx; }
.tag-warm { background: #FBF1E2; color: #A9762F; }
.tag-cool { background: #E7F2F1; color: #2E7D7B; }

.desc { display: block; margin-top: 16rpx; font-size: 25rpx; line-height: 40rpx; color: #626A75; }
.go { display: block; margin-top: 22rpx; font-size: 25rpx; font-weight: 500; }
.go-warm { color: #C58B4B; }
.go-cool { color: #2E7D7B; }

.foot { text-align: center; margin-top: 44rpx; }
.foot-link { font-size: 24rpx; color: #9AA2AC; }
</style>
