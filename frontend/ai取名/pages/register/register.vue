<template>
	<view class="page">
		<view class="wrap">
			<view class="brand">
				<view class="mark"><text class="mark-text">名</text></view>
				<text class="title">创建账号</text>
				<text class="sub">注册完就能用两个功能</text>
			</view>

			<view class="card">
				<view class="field">
					<text class="label">邮箱</text>
					<input v-model="form.email" class="input" placeholder="you@example.com" placeholder-class="ph" />
				</view>

				<view class="field">
					<text class="label">验证码</text>
					<view class="code-box">
						<input v-model="form.code" class="input code-input" placeholder="6 位验证码" placeholder-class="ph" />
						<button
							class="code-btn"
							:class="{ counting: countDown > 0 }"
							:disabled="countDown > 0 || sending"
							@click="sendCode"
						>
							{{ sending ? '发送中' : countDown > 0 ? countDown + 's' : '获取验证码' }}
						</button>
					</view>
				</view>

				<view class="field">
					<text class="label">昵称</text>
					<input v-model="form.username" class="input" placeholder="怎么称呼你" placeholder-class="ph" />
				</view>

				<view class="field">
					<view class="label-row">
						<text class="label">密码</text>
						<text class="toggle" @click="showPwd = !showPwd">{{ showPwd ? '隐藏' : '显示' }}</text>
					</view>
					<input
						v-model="form.password"
						class="input"
						:password="!showPwd"
						placeholder="至少 6 位"
						placeholder-class="ph"
					/>
				</view>

				<view class="field">
					<view class="label-row">
						<text class="label">确认密码</text>
						<text class="toggle" @click="showPwd2 = !showPwd2">{{ showPwd2 ? '隐藏' : '显示' }}</text>
					</view>
					<input
						v-model="form.confirm_password"
						class="input"
						:password="!showPwd2"
						placeholder="再输一次"
						placeholder-class="ph"
					/>
				</view>

				<button class="btn" :disabled="registering" @click="register">
					<view v-if="registering" class="spinner"></view>
					<text>{{ registering ? '注册中' : '注册' }}</text>
				</button>

				<view class="to-login" @click="goLogin">
					已有账号？<text class="link">返回登录</text>
				</view>
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
.page { min-height: 100vh; background: #F5F6F8; }
.wrap { max-width: 720rpx; margin: 0 auto; padding: 80rpx 40rpx 60rpx; }

.brand { text-align: center; margin-bottom: 48rpx; }
.mark {
	width: 88rpx; height: 88rpx; margin: 0 auto 22rpx;
	border-radius: 22rpx; background: #2E7D7B;
	display: flex; align-items: center; justify-content: center;
}
.mark-text { color: #fff; font-size: 40rpx; font-weight: 600; }
.title { display: block; font-size: 40rpx; font-weight: 600; color: #16181C; }
.sub { display: block; margin-top: 12rpx; font-size: 25rpx; color: #9AA2AC; }

.card { background: #fff; border: 2rpx solid #E6E8EB; border-radius: 24rpx; padding: 44rpx 40rpx; }

.field { margin-bottom: 30rpx; }
.label-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 14rpx; }
.label { display: block; font-size: 26rpx; color: #626A75; margin-bottom: 14rpx; }
.label-row .label { margin-bottom: 0; }
.toggle { font-size: 24rpx; color: #2E7D7B; }

.input {
	height: 88rpx; background: #F5F6F8; border: 2rpx solid #E6E8EB;
	border-radius: 16rpx; padding: 0 26rpx; font-size: 29rpx; color: #16181C;
}
.ph { color: #B4BAC2; }

.code-box { display: flex; align-items: center; gap: 16rpx; }
.code-input { flex: 1; }
.code-btn {
	width: 220rpx; height: 88rpx; line-height: 88rpx; flex-shrink: 0;
	background: #E7F2F1; color: #2E7D7B; font-size: 25rpx;
	border-radius: 16rpx; padding: 0;
}
.code-btn[disabled] { opacity: .5; }
.code-btn.counting { background: #F0F1F3; color: #9AA2AC; }

.btn {
	margin-top: 10rpx; height: 92rpx; line-height: 92rpx;
	display: flex; align-items: center; justify-content: center; gap: 14rpx;
	background: #2E7D7B; color: #fff; font-size: 30rpx; font-weight: 500;
	border-radius: 999rpx;
}
.btn[disabled] { opacity: .55; }
.spinner {
	width: 28rpx; height: 28rpx; border: 4rpx solid rgba(255,255,255,.35);
	border-top-color: #fff; border-radius: 50%; animation: spin .8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.to-login { text-align: center; margin-top: 32rpx; font-size: 26rpx; color: #9AA2AC; }
.link { color: #2E7D7B; }
</style>
