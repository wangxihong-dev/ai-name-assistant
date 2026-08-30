<template>
	<view class="page">
		<!-- 装饰光斑 -->
		<view class="blob blob-a"></view>
		<view class="blob blob-b"></view>

		<!-- 顶部品牌区 -->
		<view class="header anim-fade-up">
			<view class="logo-wrap">
				<view class="logo-orb">✨</view>
			</view>
			<text class="logo">鸿运取名</text>
			<text class="desc">AI 国学智能命名助手</text>
			<text class="wish">愿每一个名字，都承载父母的祝福</text>
		</view>

		<!-- 登录卡片 -->
		<view class="card anim-fade-up" :style="{ animationDelay: '80ms' }">
			<text class="card-title">欢迎回来</text>

			<view class="field">
				<text class="label">邮箱</text>
				<view class="input-wrap">
					<text class="input-icon">✉</text>
					<input
						v-model="form.email"
						class="input"
						type="text"
						placeholder="请输入邮箱"
						placeholder-class="ph"
					/>
				</view>
			</view>

			<view class="field">
				<text class="label">密码</text>
				<view class="input-wrap">
					<text class="input-icon">🔒</text>
					<input
						v-model="form.password"
						class="input"
						:password="!showPwd"
						placeholder="请输入密码"
						placeholder-class="ph"
					/>
					<text class="eye" @click="showPwd = !showPwd">{{ showPwd ? '🙈' : '👁' }}</text>
				</view>
			</view>

			<button class="login-btn" :disabled="loading" @click="login">
				<view v-if="loading" class="spinner"></view>
				<text>{{ loading ? '正在登录...' : '开始探索名字' }}</text>
			</button>

			<view class="register" @click="goRegister">
				还没有账号？<text class="link">立即注册</text>
			</view>
		</view>

		<text class="footer-note">诗经 · 楚辞 · 唐诗宋词</text>
	</view>
</template>

<script setup>
import { ref } from "vue"
import API from "../../common/api.js"

const form = ref({
	email: "",
	password: ""
})
const showPwd = ref(false)
const loading = ref(false)

const login = async () => {
	if (!form.value.email || !form.value.password) {
		uni.showToast({ title: "请输入完整信息", icon: "none" })
		return
	}
	if (loading.value) return // 防重复提交

	loading.value = true
	try {
		const data = await API.login(form.value)
		if (data && data.tokens) {
			uni.setStorageSync("token", data.tokens)
			uni.showToast({ title: "登录成功", icon: "success" })
			setTimeout(() => {
				uni.reLaunch({ url: "/pages/name/name" })
			}, 700)
		} else {
			uni.showToast({ title: "登录失败，请检查邮箱和密码", icon: "none" })
		}
	} catch (e) {
		uni.showToast({ title: e.message || "登录失败", icon: "none" })
	} finally {
		loading.value = false
	}
}

const goRegister = () => {
	uni.navigateTo({ url: "/pages/register/register" })
}
</script>

<style>
.page {
	min-height: 100vh;
	background: linear-gradient(180deg, #FFF4E0 0%, #FAF4EA 60%);
	padding: 120rpx 40rpx 60rpx;
	position: relative;
	overflow: hidden;
}

/* 装饰光斑 */
.blob {
	position: absolute;
	border-radius: 50%;
	filter: blur(4rpx);
	opacity: 0.55;
	pointer-events: none;
}

.blob-a {
	width: 320rpx;
	height: 320rpx;
	top: -90rpx;
	right: -80rpx;
	background: radial-gradient(circle, rgba(232, 185, 107, 0.55), rgba(232, 185, 107, 0));
	animation: float 6s ease-in-out infinite;
}

.blob-b {
	width: 260rpx;
	height: 260rpx;
	left: -90rpx;
	top: 42%;
	background: radial-gradient(circle, rgba(217, 140, 122, 0.4), rgba(217, 140, 122, 0));
	animation: float 7s ease-in-out infinite reverse;
}

.header {
	text-align: center;
	margin-bottom: 70rpx;
	position: relative;
}

.logo-wrap {
	display: flex;
	justify-content: center;
	margin-bottom: 22rpx;
}

.logo-orb {
	width: 120rpx;
	height: 120rpx;
	border-radius: 50%;
	background: linear-gradient(135deg, #E8B96B, #C58B4B);
	display: flex;
	align-items: center;
	justify-content: center;
	font-size: 56rpx;
	box-shadow: 0 18rpx 40rpx rgba(197, 139, 75, 0.4);
	animation: float 4s ease-in-out infinite;
}

.logo {
	display: block;
	font-size: 58rpx;
	font-weight: bold;
	background: linear-gradient(135deg, #9B6B3C, #C58B4B);
	-webkit-background-clip: text;
	background-clip: text;
	color: transparent;
}

.desc {
	display: block;
	font-size: 30rpx;
	color: #8C735C;
	margin-top: 18rpx;
	letter-spacing: 4rpx;
}

.wish {
	display: block;
	margin-top: 34rpx;
	color: #B9A48E;
	font-size: 26rpx;
	line-height: 44rpx;
}

/* 卡片 */
.card {
	background: rgba(255, 255, 255, 0.9);
	border-radius: 40rpx;
	padding: 56rpx 44rpx;
	box-shadow: 0 20rpx 60rpx rgba(154, 107, 60, 0.14);
	border: 2rpx solid rgba(232, 185, 107, 0.18);
	position: relative;
}

.card-title {
	display: block;
	font-size: 38rpx;
	font-weight: bold;
	color: #4A3728;
	margin-bottom: 44rpx;
}

.field {
	margin-bottom: 36rpx;
}

.label {
	display: block;
	color: #8C735C;
	margin-bottom: 14rpx;
	font-size: 26rpx;
	font-weight: bold;
}

.input-wrap {
	display: flex;
	align-items: center;
	height: 96rpx;
	background: #FFF9F0;
	border-radius: 24rpx;
	padding: 0 26rpx;
	border: 2rpx solid #F0E6D6;
	transition: border-color 0.25s;
}

.input-icon {
	font-size: 28rpx;
	margin-right: 16rpx;
}

.input {
	flex: 1;
	height: 96rpx;
	font-size: 30rpx;
	color: #4A3728;
}

.ph {
	color: #C9BBA4;
}

.eye {
	font-size: 30rpx;
	padding-left: 16rpx;
}

.login-btn {
	margin-top: 16rpx;
	height: 100rpx;
	line-height: 100rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	gap: 16rpx;
	background: linear-gradient(135deg, #E8B96B, #C58B4B);
	color: #fff;
	font-size: 32rpx;
	font-weight: bold;
	border-radius: 999rpx;
	box-shadow: 0 16rpx 32rpx rgba(197, 139, 75, 0.35);
}

.login-btn[disabled] {
	opacity: 0.75;
}

.spinner {
	width: 30rpx;
	height: 30rpx;
	border: 4rpx solid rgba(255, 255, 255, 0.4);
	border-top-color: #fff;
	border-radius: 50%;
	animation: spin 0.8s linear infinite;
}

.register {
	text-align: center;
	margin-top: 40rpx;
	color: #B9A48E;
	font-size: 26rpx;
}

.link {
	color: #C58B4B;
	font-weight: bold;
}

.footer-note {
	display: block;
	text-align: center;
	margin-top: 56rpx;
	color: #C9BBA4;
	font-size: 24rpx;
	letter-spacing: 6rpx;
}
</style>
