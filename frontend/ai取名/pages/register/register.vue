<template>

<view class="page">


	<view class="logo">

		<text class="title">
			✨ 鸿运取名
		</text>

		<text class="sub">
			为宝宝寻找一个美好的名字
		</text>

	</view>



	<view class="card">


		<input
			v-model="form.email"
			class="input"
			placeholder="请输入您的邮箱"
		/>


		<view class="code-box">


			<input
				v-model="form.code"
				class="code-input"
				placeholder="邮箱验证码"
			/>


			<button
				class="code-btn"
				@click="sendCode"
				:disabled="countDown>0 || sending"
			>

			{{sending?'发送中...':countDown>0?
			countDown+'秒后重发':
			'获取验证码'}}


			</button>


		</view>



		<input
			v-model="form.username"
			class="input"
			placeholder="请输入昵称"
		>



		<input
			v-model="form.password"
			password
			class="input"
			placeholder="设置密码"
		>



		<input
			v-model="form.confirm_password"
			password
			class="input"
			placeholder="确认密码"
		>



		<button
			class="main-btn"
			@click="register"
		>

		注册账号

		</button>



	</view>



</view>

</template>



<script setup>


import {ref} from "vue"



const form=ref({

	email:"",
	username:"",
	password:"",
	confirm_password:"",
	code:""

})



const countDown=ref(0)
const sending=ref(false)
let timer=null

// 邮箱格式校验
const isValidEmail=(email)=>{
	const reg=/^[^\s@]+@[^\s@]+\.[^\s@]+$/
	return reg.test(email)
}

// 获取验证码
const sendCode=()=>{

	// 1. 校验邮箱
	if(!form.value.email){
		uni.showToast({
			title:"请先输入邮箱",
			icon:"none"
		})
		return
	}

	if(!isValidEmail(form.value.email)){
		uni.showToast({
			title:"邮箱格式不正确",
			icon:"none"
		})
		return
	}

	// 2. 防止重复点击
	if(sending.value || countDown.value>0){
		return
	}

	sending.value=true

	// 3. 发送请求
	uni.request({

		url:"http://127.0.0.1:8000/auth/code",
		method:"GET",
		data:{
			email:form.value.email
		},

		success(res){
			// 请求成功（HTTP 200）
			if(res.statusCode===200){
				uni.showToast({
					title:"验证码已发送，请注意查收",
					icon:"none"
				})
				// 开始倒计时
				startCountDown()
			}else{
				// 后端返回错误
				const msg=res.data?.detail || "发送失败，请重试"
				uni.showToast({
					title:msg,
					icon:"none"
				})
			}
		},

		fail(err){
			// 请求失败（网络错误、后端没启动等）
			console.log("验证码发送失败:",err)
			uni.showToast({
				title:"网络错误，请检查后端是否启动",
				icon:"none"
			})
		},

		complete(){
			sending.value=false
		}

	})
}

// 倒计时
const startCountDown=()=>{
	countDown.value=60
	if(timer){
		clearInterval(timer)
	}
	timer=setInterval(()=>{
		countDown.value--
		if(countDown.value<=0){
			clearInterval(timer)
			timer=null
		}
	},1000)
}




const register=()=>{

	// 简单校验
	if(!form.value.email || !form.value.code || !form.value.username || !form.value.password){
		uni.showToast({
			title:"请填写完整信息",
			icon:"none"
		})
		return
	}

	if(form.value.password !== form.value.confirm_password){
		uni.showToast({
			title:"两次密码不一致",
			icon:"none"
		})
		return
	}

	uni.request({

		url:"http://127.0.0.1:8000/auth/register",
		method:"POST",
		data:form.value,

		success(res){
			if(res.statusCode===200){
				uni.showToast({
					title:"注册成功，请登录"
				})
				setTimeout(()=>{
					uni.navigateBack()
				},1000)
			}else{
				const msg=res.data?.detail || "注册失败，请重试"
				uni.showToast({
					title:msg,
					icon:"none"
				})
			}
		},

		fail(){
			uni.showToast({
				title:"网络错误，请检查后端是否启动",
				icon:"none"
			})
		}

	})


}



</script>



<style>


.page{

	min-height:100vh;

	background:#fff8ed;

	padding:60rpx 40rpx;

}



.logo{

	text-align:center;

	margin-bottom:60rpx;

}


.title{

	display:block;

	font-size:52rpx;

	color:#8b5e34;

	font-weight:bold;

}


.sub{

	color:#aa8866;

	margin-top:20rpx;

}



.card{

	background:white;

	border-radius:40rpx;

	padding:50rpx;

	box-shadow:
	0 10rpx 30rpx rgba(0,0,0,.08);

}



.input,
.code-input{

	height:90rpx;

	border-bottom:
	1px solid #eee;

	margin-bottom:30rpx;

}



.code-box{

	display:flex;

	align-items:center;

}


.code-input{

	flex:1;

}



.code-btn{

	font-size:24rpx;

	background:#f5d6a1;

	color:#8b5e34;

}


.main-btn{

	margin-top:40rpx;

	background:#c98b4b;

	color:white;

	border-radius:50rpx;

}


</style>