<template>

<view class="page">


	<!-- 顶部Logo -->

	<view class="header">


		<text class="logo">
			✨ 鸿运取名
		</text>


		<text class="desc">
			AI国学智能命名助手
		</text>


		<text class="wish">
			愿每一个名字，
			都承载父母的祝福
		</text>


	</view>



	<!-- 登录卡片 -->


	<view class="card">


		<view class="item">


			<text class="label">
				邮箱
			</text>


			<input
				v-model="form.email"
				placeholder="请输入邮箱"
			/>


		</view>




		<view class="item">


			<text class="label">
				密码
			</text>


			<input
				v-model="form.password"
				password
				placeholder="请输入密码"
			/>


		</view>




		<button
			class="login-btn"
			@click="login"
		>

			开始探索名字

		</button>



		<view
			class="register"
			@click="goRegister"
		>

			还没有账号？
			<text>
				立即注册
			</text>


		</view>



	</view>



</view>


</template>



<script setup>


import {ref} from "vue"



const form=ref({

	email:"",
	password:""

})




//登录

const login=()=>{


	if(!form.value.email ||
	   !form.value.password){


		uni.showToast({

			title:"请输入完整信息",

			icon:"none"

		})


		return

	}




	uni.request({


		url:"http://127.0.0.1:8000/auth/login",


		method:"POST",


		data:form.value,



		success(res){


			console.log(res.data)



			//保存token

			uni.setStorageSync(
				"token",
				res.data.tokens
			)



			uni.showToast({

				title:"登录成功"

			})



			setTimeout(()=>{


				uni.reLaunch({

					url:"/pages/name/name"

				})


			},1000)



		},


		fail(){


			uni.showToast({

				title:"登录失败",

				icon:"none"

			})


		}


	})


}




const goRegister=()=>{


	uni.navigateTo({

		url:"/pages/register/register"

	})


}


</script>




<style>


.page{

	min-height:100vh;

	background:#fff7eb;

	padding:80rpx 40rpx;

}




.header{

	text-align:center;

	margin-bottom:70rpx;

}



.logo{

	display:block;

	font-size:56rpx;

	font-weight:bold;

	color:#9b6b3c;

}



.desc{

	display:block;

	font-size:34rpx;

	color:#b38b62;

	margin-top:20rpx;

}



.wish{

	display:block;

	margin-top:40rpx;

	color:#8c735c;

	line-height:50rpx;

}





.card{

	background:white;

	padding:50rpx;

	border-radius:40rpx;


	box-shadow:

	0 15rpx 40rpx rgba(150,100,50,.12);


}



.item{

	margin-bottom:40rpx;

}



.label{

	display:block;

	color:#8b5e34;

	margin-bottom:15rpx;

	font-size:30rpx;

}



input{


	height:90rpx;

	background:#fffaf3;

	border-radius:20rpx;

	padding:0 25rpx;

}




.login-btn{


	margin-top:40rpx;

	background:#c58b4b;

	color:white;

	border-radius:50rpx;


}



.register{


	text-align:center;

	margin-top:40rpx;

	color:#999;

}



.register text{


	color:#c58b4b;


}



</style>