<script>
	export default {
		onLaunch: function() {
			console.log('App Launch')
		},
		onShow: function() {
			console.log('App Show')
		},
		onHide: function() {
			console.log('App Hide')
		}
	}
</script>

<style>
	/* ============ 全局设计系统 ============ */
	/* 暖色高级感配色：奶油底 + 焦糖金 + 深咖文字 */
	page {
		--bg: #FAF4EA;
		--bg-soft: #FFF9F0;
		--card: #FFFFFF;
		--primary: #C58B4B;
		--primary-deep: #9B6B3C;
		--accent: #E8B96B;
		--accent-soft: #F6E3C8;
		--rose: #D98C7A;
		--text: #4A3728;
		--text-2: #8C735C;
		--text-3: #B9A48E;
		--line: #F0E6D6;
		--shadow-sm: 0 8rpx 24rpx rgba(154, 107, 60, 0.08);
		--shadow-md: 0 16rpx 48rpx rgba(154, 107, 60, 0.14);
		--grad: linear-gradient(135deg, #E8B96B 0%, #C58B4B 100%);
		--grad-soft: linear-gradient(160deg, #FFF9F0 0%, #F8ECD8 100%);

		background: var(--bg);
		color: var(--text);
		font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", sans-serif;
	}

	/* ============ 公共入场动画（只用 transform/opacity，GPU 友好） ============ */
	@keyframes fadeUp {
		from { opacity: 0; transform: translateY(28rpx); }
		to { opacity: 1; transform: translateY(0); }
	}

	@keyframes fadeIn {
		from { opacity: 0; }
		to { opacity: 1; }
	}

	@keyframes float {
		0%, 100% { transform: translateY(0); }
		50% { transform: translateY(-14rpx); }
	}

	@keyframes spin {
		from { transform: rotate(0deg); }
		to { transform: rotate(360deg); }
	}

	@keyframes pulse {
		0%, 100% { opacity: 1; transform: scale(1); }
		50% { opacity: 0.55; transform: scale(1.08); }
	}

	@keyframes shimmer {
		0% { background-position: -400rpx 0; }
		100% { background-position: 400rpx 0; }
	}

	.anim-fade-up {
		animation: fadeUp 0.5s ease both;
	}

	.anim-fade-in {
		animation: fadeIn 0.4s ease both;
	}

	/* ============ 骨架屏占位 ============ */
	.skeleton {
		background: linear-gradient(90deg, #F3EAD9 25%, #FAF3E6 50%, #F3EAD9 75%);
		background-size: 800rpx 100%;
		animation: shimmer 1.4s infinite linear;
		border-radius: 16rpx;
	}
</style>
