<template>
	<view class="page">
		<view class="blob blob-a"></view>
		<view class="blob blob-b"></view>

		<!-- 顶部 -->
		<view class="header anim-fade-up">
			<text class="logo">✨ 鸿运取名</text>
			<text class="sub">为宝宝寻找一个美好的名字</text>
		</view>

		<!-- 注册卡片 -->
		<view class="card anim-fade-up" :style="{ animationDelay: '80ms' }">
			<text class="card-title">创建账号</text>

			<view class="field">
				<text class="label">邮箱</text>
				<view class="input-wrap">
					<text class="input-icon">✉</text>
					<input v-model="form.email" class="input" placeholder="请输入您的邮箱" placeholder-class="ph" />
				</view>
			</view>

			<view class="field">
				<text class="label">验证码</text>
				<view class="code-box">
					<view class="input-wrap code-input-wrap">
						<text class="input-icon">✎</text>
						<input v-model="form.code" class="input" placeholder="邮箱验证码" placeholder-class="ph" />
					</view>
					<button
						class="code-btn"
						:class="{ counting: countDown > 0 }"
						:disabled="countDown > 0 || sending"
						@click="sendCode"
					>
						{{ sending ? '发送中...' : countDown > 0 ? countDown + 's' : '获取验证码' }}
					</button>
				</view>
			</view>

			<view class="field">
				<text class="label">昵称</text>
				<view class="input-wrap">
					<text class="input-icon">👤</text>
					<input v-model="form.username" class="input" placeholder="请输入昵称" placeholder-class="ph" />
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
						placeholder="设置密码（至少 6 位）"
						placeholder-class="ph"
					/>
					<text class="eye" @click="showPwd = !showPwd">{{ showPwd ? '🙈' : '👁' }}</text>
				</view>
			</view>

			<view class="field">
				<text class="label">确认密码</text>
				<view class="input-wrap">
					<text class="input-icon">🔒</text>
					<input
						v-model="form.confirm_password"
						class="input"
						:password="!showPwd2"
						placeholder="再次输入密码"
						placeholder-class="ph"
					/>
					<text class="eye" @click="showPwd2 = !showPwd2">{{ showPwd2 ? '🙈' : '👁' }}</text>
				</view>
			</view>

			<button class="main-btn" :disabled="registering" @click="register">
				<view v-if="registering" class="spinner"></view>
				<text>{{ registering ? '正在注册...' : '注册账号' }}</text>
			</button>

			<view class="to-login" @click="goLogin">
				已有账号？<text class="link">返回登录</text>
			</view>
		</view>
	</view>
</template>

<script setup>
import { ref, onUnmounted } from "vue"
import API from "../../common/api.js"

const form = ref({
	email: "",
	username: "",
	password: "",
	confirm_password: "",
	code: ""
})
const countDown = ref(0)
const sending = ref(false)
const registering = ref(false)
const showPwd = ref(false)
const showPwd2 = ref(false)
let timer = null

// 邮箱格式校验
const isValidEmail = (email) => {
	return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
}

// 获取验证码
const sendCode = async () => {
	if (!form.value.email) {
		uni.showToast({ title: "请先输入邮箱", icon: "none" })
		return
	}
	if (!isValidEmail(form.value.email)) {
		uni.showToast({ title: "邮箱格式不正确", icon: "none" })
		return
	}
	if (sending.value || countDown.value > 0) return

	sending.value = true
	try {
		await API.sendCode(form.value.email)
		uni.showToast({ title: "验证码已发送", icon: "none" })
		startCountDown()
	} catch (e) {
		uni.showToast({ title: e.message || "发送失败，请重试", icon: "none" })
	} finally {
		sending.value = false
	}
}

// 倒计时
const startCountDown = () => {
	countDown.value = 60
	if (timer) clearInterval(timer)
	timer = setInterval(() => {
		countDown.value--
		if (countDown.value <= 0) {
			clearInterval(timer)
			timer = null
		}
	}, 1000)
}

// 注册
const register = async () => {
	if (!form.value.email || !form.value.code || !form.value.username || !form.value.password) {
		uni.showToast({ title: "请填写完整信息", icon: "none" })
		return
	}
	if (form.value.password !== form.value.confirm_password) {
		uni.showToast({ title: "两次密码不一致", icon: "none" })
		return
	}
	if (form.value.password.length < 6) {
		uni.showToast({ title: "密码至少 6 位", icon: "none" })
		return
	}
	if (registering.value) return

	registering.value = true
	try {
		await API.register(form.value)
		uni.showToast({ title: "注册成功，请登录", icon: "success" })
		setTimeout(() => uni.navigateBack(), 700)
	} catch (e) {
		uni.showToast({ title: e.message || "注册失败，请重试", icon: "none" })
	} finally {
		registering.value = false
	}
}

const goLogin = () => {
	uni.navigateBack()
}

onUnmounted(() => {
	if (timer) clearInterval(timer)
})
</script>

<style>
.page {
	min-height: 100vh;
	background: linear-gradient(180deg, #FFF4E0 0%, #FAF4EA 55%);
	padding: 90rpx 40rpx 70rpx;
	position: relative;
	overflow: hidden;
}

.blob {
	position: absolute;
	border-radius: 50%;
	opacity: 0.5;
	pointer-events: none;
}

.blob-a {
	width: 300rpx;
	height: 300rpx;
	top: -80rpx;
	left: -80rpx;
	background: radial-gradient(circle, rgba(232, 185, 107, 0.5), rgba(232, 185, 107, 0));
	animation: float 6s ease-in-out infinite;
}

.blob-b {
	width: 240rpx;
	height: 240rpx;
	right: -80rpx;
	top: 46%;
	background: radial-gradient(circle, rgba(217, 140, 122, 0.38), rgba(217, 140, 122, 0));
	animation: float 7s ease-in-out infinite reverse;
}

.header {
	text-align: center;
	margin-bottom: 54rpx;
	position: relative;
}

.logo {
	display: block;
	font-size: 50rpx;
	font-weight: bold;
	background: linear-gradient(135deg, #9B6B3C, #C58B4B);
	-webkit-background-clip: text;
	background-clip: text;
	color: transparent;
}

.sub {
	display: block;
	color: #B9A48E;
	margin-top: 18rpx;
	font-size: 26rpx;
}

.card {
	background: rgba(255, 255, 255, 0.92);
	border-radius: 40rpx;
	padding: 50rpx 44rpx;
	box-shadow: 0 20rpx 60rpx rgba(154, 107, 60, 0.14);
	border: 2rpx solid rgba(232, 185, 107, 0.18);
	position: relative;
}

.card-title {
	display: block;
	font-size: 38rpx;
	font-weight: bold;
	color: #4A3728;
	margin-bottom: 40rpx;
}

.field {
	margin-bottom: 32rpx;
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
	height: 94rpx;
	background: #FFF9F0;
	border-radius: 24rpx;
	padding: 0 26rpx;
	border: 2rpx solid #F0E6D6;
}

.input-icon {
	font-size: 28rpx;
	margin-right: 16rpx;
}

.input {
	flex: 1;
	height: 94rpx;
	font-size: 29rpx;
	color: #4A3728;
}

.ph {
	color: #C9BBA4;
}

.eye {
	font-size: 30rpx;
	padding-left: 16rpx;
}

.code-box {
	display: flex;
	align-items: stretch;
	gap: 18rpx;
}

.code-input-wrap {
	flex: 1;
}

.code-btn {
	flex-shrink: 0;
	margin: 0;
	width: 220rpx;
	height: 94rpx;
	line-height: 94rpx;
	font-size: 25rpx;
	color: #9B6B3C;
	background: #FBF0DE;
	border-radius: 24rpx;
	border: 2rpx solid #F0E6D6;
	transition: all 0.25s;
}

.code-btn.counting {
	background: #F6E3C8;
	color: #B9A48E;
	animation: pulse 1s ease-in-out infinite;
}

.code-btn[disabled] {
	opacity: 1;
}

.main-btn {
	margin-top: 20rpx;
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

.main-btn[disabled] {
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

.to-login {
	text-align: center;
	margin-top: 36rpx;
	color: #B9A48E;
	font-size: 26rpx;
}

.link {
	color: #C58B4B;
	font-weight: bold;
}
</style>
