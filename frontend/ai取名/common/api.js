// =============================================
// 统一请求层：基础地址、鉴权、超时、错误处理
// 使用方式：import API from "@/common/api"（或相对路径）
// =============================================

// 后端基础地址（部署时只需改这一处）
const BASE_URL = "http://127.0.0.1:8000"

// 读取本地缓存的 token
const getToken = () => {
	try {
		return uni.getStorageSync("token")
	} catch (e) {
		return ""
	}
}

// 通用请求函数：返回 Promise，成功 resolve 响应体，失败 reject Error
export const request = (options) => {
	return new Promise((resolve, reject) => {
		const {
			url,
			method = "GET",
			data = {},
			auth = true,      // 是否需要登录鉴权
			timeout = 30000   // 统一 30 秒超时
		} = options

		const header = { "Content-Type": "application/json" }
		const token = getToken()
		if (auth && token) {
			header.Authorization = "Bearer " + token
		}

		uni.request({
			url: BASE_URL + url,
			method,
			data,
			timeout,
			header,
			success: (res) => {
				// 2xx 视为成功，直接返回后端数据
				if (res.statusCode >= 200 && res.statusCode < 300) {
					resolve(res.data)
					return
				}
				// 401/403：登录失效统一处理
				if (res.statusCode === 401 || res.statusCode === 403) {
					try { uni.removeStorageSync("token") } catch (e) {}
					uni.showToast({ title: "登录已过期，请重新登录", icon: "none" })
					setTimeout(() => {
						uni.reLaunch({ url: "/pages/index/index" })
					}, 900)
				}
				const msg = (res.data && (res.data.detail || res.data.message)) || `请求失败(${res.statusCode})`
				reject(new Error(msg))
			},
			fail: () => {
				reject(new Error("网络错误，请检查后端是否启动"))
			}
		})
	})
}

// 按业务分组的接口集合：所有页面统一从这里调用
export const API = {
	// 认证
	login: (data) => request({ url: "/auth/login", method: "POST", data, auth: false }),
	sendCode: (email) => request({ url: "/auth/code", method: "GET", data: { email }, auth: false }),
	register: (data) => request({ url: "/auth/register", method: "POST", data, auth: false }),

	// 取名与历史
	generateName: (data) => request({ url: "/name/", method: "POST", data }),
	getHistory: () => request({ url: "/name/history", method: "GET" }),

	// 收藏
	addFavorite: (data) => request({ url: "/name/favorite", method: "POST", data }),
	getFavorites: () => request({ url: "/name/favorites", method: "GET" }),
	removeFavorite: (id) => request({ url: `/name/delete/${id}`, method: "DELETE" })
}

export default API
