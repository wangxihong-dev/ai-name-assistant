<template>

<view class="page">


	<!-- 顶部区域 -->

	<view class="header">

		<text class="logo">
			✨ 鸿运取名
		</text>


		<text class="subtitle">
			AI国学智能命名助手
		</text>


		<text class="desc">
			结合诗经、楚辞、唐诗宋词
			为宝宝寻找寓意美好的名字
		</text>


	</view>



	<!-- 输入卡片 -->

	<view class="card">


		<text class="label">
			宝宝姓氏
		</text>


		<input
			v-model="form.surname"
			class="input"
			placeholder="例如：李"
		/>




		<text class="label">
			宝宝性别
		</text>


		<view class="select-box">


			<button
				@click="form.gender='男'"
				:class="{active:form.gender==='男'}"
			>
				男孩
			</button>



			<button
				@click="form.gender='女'"
				:class="{active:form.gender==='女'}"
			>
				女孩
			</button>


		</view>




		<text class="label">
			名字长度
		</text>



		<view class="select-box">


			<button
				@click="form.length='两字'"
				:class="{active:form.length==='两字'}"
			>
				单字名
			</button>



			<button
				@click="form.length='三字'"
				:class="{active:form.length==='三字'}"
			>
				双字名
			</button>



		</view>





		<text class="label">
			父母寄语
		</text>


		<textarea
			v-model="form.other"
			class="textarea"
			placeholder="例如：希望孩子温柔、有智慧、平安快乐"
		/>


		<button
			class="generate"
			@click="generate"
			:disabled="loading"
		>

			{{loading?'AI正在取名...':'✨ 开始取名'}}

		</button>



	</view>





	<!-- AI等待动画 -->


	<view
		v-if="loading"
		class="loading-box"
	>


		<view class="magic">

			✨

		</view>


		<text class="loading-title">

			AI正在为宝宝寻找好名字

		</text>


		<text class="loading-desc">

			正在翻阅诗经、楚辞、唐诗宋词...

		</text>



		<text class="loading-desc">

			请耐心等待几秒钟

		</text>



	</view>







	<!-- 结果区域 -->


	<view
		v-if="result"
		class="result"
	>


		<text class="result-title">

			🎉 AI推荐名字

		</text>



		<view
			v-for="item in result.names"
			:key="item.name"
			class="name-card"
		>


			<text class="name">

				{{item.name}}

			</text>



			<view class="line"></view>



			<text class="info">

				📖 出处

			</text>


			<text class="content">

				{{item.reference}}

			</text>




			<text class="info">

				🌱 寓意

			</text>


			<text class="content">

				{{item.moral}}

			</text>



			<button class="save">

				❤️ 收藏名字

			</button>



		</view>


	</view>



</view>


</template>





<script setup>


import {
	ref
} from "vue"





const form=ref({

	surname:"",

	gender:"",

	length:"三字",

	other:"",

	exclude:[]

})



const loading=ref(false)


const result=ref(null)





const generate=()=>{


	if(!form.value.surname){

		uni.showToast({

			title:"请输入宝宝姓氏",

			icon:"none"

		})

		return

	}



	if(!form.value.gender){

		uni.showToast({

			title:"请选择宝宝性别",

			icon:"none"

		})

		return

	}




	const token=
	uni.getStorageSync("token")



	loading.value=true

	result.value=null



	uni.request({


		url:"http://127.0.0.1:8000/name/",


		method:"POST",


		data:form.value,


		header:{


			Authorization:
			"Bearer "+token


		},



		success(res){


			console.log(res.data)


			result.value=res.data


		},



		fail(){

			uni.showToast({

				title:"生成失败",

				icon:"none"

			})

		},



		complete(){

			loading.value=false

		}


	})



}



</script>





<style>


.page{


	min-height:100vh;

	background:#fff7eb;

	padding:50rpx 35rpx;


}



.header{


	text-align:center;

	margin-bottom:50rpx;


}



.logo{


	display:block;

	font-size:55rpx;

	font-weight:bold;

	color:#946638;


}



.subtitle{


	display:block;

	margin-top:20rpx;

	font-size:35rpx;

	color:#b88655;


}



.desc{


	display:block;

	margin-top:25rpx;

	color:#8c735c;

	line-height:45rpx;


}




.card{


	background:white;

	border-radius:40rpx;

	padding:45rpx;


}



.label{


	display:block;

	margin:30rpx 0 15rpx;

	color:#8b5e34;


}



.input{


	background:#fffaf3;

	border-radius:20rpx;

	padding:20rpx;


}



.select-box{


	display:flex;

	gap:30rpx;


}



.select-box button{


	flex:1;

	background:#f8ead7;

	border-radius:30rpx;


}



.active{


	background:#c58b4b!important;

	color:white;


}




.textarea{


	margin-top:10rpx;

	background:#fffaf3;

	border-radius:20rpx;

	padding:20rpx;

	height:180rpx;


}



.generate{


	margin-top:50rpx;

	background:#c58b4b;

	color:white;

	border-radius:50rpx;


}






.loading-box{


	margin-top:40rpx;

	background:white;

	border-radius:40rpx;

	padding:60rpx;

	text-align:center;


}




.magic{


	font-size:90rpx;

}



.loading-title{


	display:block;

	font-size:38rpx;

	color:#946638;

	margin-top:30rpx;


}



.loading-desc{


	display:block;

	margin-top:20rpx;

	color:#999;


}




.result{


	margin-top:50rpx;


}




.result-title{


	font-size:40rpx;

	color:#946638;


}




.name-card{


	margin-top:30rpx;

	background:white;

	padding:40rpx;

	border-radius:40rpx;


}




.name{


	display:block;

	text-align:center;

	font-size:70rpx;

	font-weight:bold;

	color:#c58b4b;


}



.line{


	height:2rpx;

	background:#eee;

	margin:30rpx 0;


}



.info{


	display:block;

	color:#946638;

	font-size:30rpx;

	margin-top:20rpx;

	font-weight:bold;


}



.content{


	display:block;

	color:#666;

	line-height:45rpx;

	margin-top:10rpx;


}



.save{


	margin-top:30rpx;

	background:#f5dfc2;

	color:#946638;

	border-radius:40rpx;


}



</style>