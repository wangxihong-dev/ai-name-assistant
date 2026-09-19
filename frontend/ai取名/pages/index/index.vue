<template>
	<view class="page">
		<view class="wrap">
			<!-- 品牌区：一个 CSS 画的方形标记，不用 emoji -->
			<view class="brand">
				<view class="mark"><text class="mark-text">名</text></view>
				<text class="title">鸿运取名</text>
				<text class="sub">登录后即可使用宝宝取名与品牌取名</text>
			</view>

			<view class="card">
				<view class="field">
					<text class="label">邮箱</text>
					<input
						v-model="form.email"
						class="input"
						type="text"
						placeholder="you@example.com"
						placeholder-class="ph"
					/>
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
						placeholder="请输入密码"
						placeholder-class="ph"
					/>
				</view>

				<button class="btn" :disabled="loading" @click="login">
					<view v-if="loading" class="spinner"></view>
					<text>{{ loading ? '登录中' : '登录' }}</text>
				</button>

				<view class="to-register" @click="goRegister">
					还没有账号？<text class="link">注册一个</text>
				</view>
			</view>

			<view class="foot">
				<text class="foot-link" @click="goPortal">← 返回门户</text>
			</view>
		</view>
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
				uni.reLaunch({ url: "/pages/select/select" })
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

// 门户是 nginx 直接托管的静态页，不在 uni-app 的路由里，所以只能整页跳
const goPortal = () => {
	// #ifdef H5
	window.location.href = "/"
	// #endif
	// #ifndef H5
	uni.showToast({ title: "请在浏览器里访问站点根路径", icon: "none" })
	// #endif
}
</script>

<style>
.page { min-height: 100vh; background: #F5F6F8; }
.wrap { max-width: 720rpx; margin: 0 auto; padding: 130rpx 40rpx 60rpx; }

.brand { text-align: center; margin-bottom: 64rpx; }
.mark {
	width: 96rpx; height: 96rpx; margin: 0 auto 26rpx;
	border-radius: 24rpx; background: #2E7D7B;
	display: flex; align-items: center; justify-content: center;
}
.mark-text { color: #fff; font-size: 44rpx; font-weight: 600; }
.title { display: block; font-size: 44rpx; font-weight: 600; color: #16181C; letter-spacing: 2rpx; }
.sub { display: block; margin-top: 14rpx; font-size: 26rpx; color: #9AA2AC; }

.card { background: #fff; border: 2rpx solid #E6E8EB; border-radius: 24rpx; padding: 48rpx 40rpx; }

.field { margin-bottom: 34rpx; }
.label-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 14rpx; }
.label { display: block; font-size: 26rpx; color: #626A75; margin-bottom: 14rpx; }
.label-row .label { margin-bottom: 0; }
.toggle { font-size: 24rpx; color: #2E7D7B; }

.input {
	height: 92rpx; background: #F5F6F8; border: 2rpx solid #E6E8EB;
	border-radius: 16rpx; padding: 0 26rpx; font-size: 29rpx; color: #16181C;
}
.ph { color: #B4BAC2; }

.btn {
	margin-top: 12rpx; height: 92rpx; line-height: 92rpx;
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

.to-register { text-align: center; margin-top: 34rpx; font-size: 26rpx; color: #9AA2AC; }
.link { color: #2E7D7B; }

.foot { text-align: center; margin-top: 48rpx; }
.foot-link { font-size: 24rpx; color: #B4BAC2; }
</style>
