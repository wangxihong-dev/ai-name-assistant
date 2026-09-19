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
	removeFavorite: (id) => request({ url: `/name/delete/${id}`, method: "DELETE" }),

	// 对话版
	chat: (data) => request({ url: "/chat/", method: "POST", timeout: 120000, data }),
	chatHistory: (id) => request({ url: `/chat/${id}/history`, method: "GET" })
}



// =============================================
// 对话版：普通接口走 request()，流式接口必须绕开它
//
// uni.request 不支持流式响应——它要等整个响应体收完才回调 success，
// 那样 SSE 就退化成普通请求了，进度事件全攒到最后一次性到。
// 所以 H5 端直接用浏览器原生 fetch + ReadableStream 自己读。
// 小程序端要用 uni.request 的 enableChunked，写法完全不同，这一版不做，
// 非 H5 端回落到普通接口 API.chat()。
// =============================================

// 把一段 SSE 文本块解析成 { event, data }
const parseSseBlock = (block) => {
	let event = "message"
	const dataLines = []
	block.split("\n").forEach((raw) => {
		const line = raw.replace(/\r$/, "")
		if (line.startsWith("event:")) {
			event = line.slice(6).trim()
		} else if (line.startsWith("data:")) {
			dataLines.push(line.slice(5).trim())
		}
	})
	if (!dataLines.length) return null
	try {
		return { event, data: JSON.parse(dataLines.join("\n")) }
	} catch (e) {
		return null
	}
}

// #ifdef H5
const runH5Stream = async ({ userInput, conversationId, onStage, onResult, onError }, controller) => {
	try {
		const resp = await fetch(BASE_URL + "/chat/stream", {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
				"Authorization": "Bearer " + getToken()
			},
			body: JSON.stringify({ user_input: userInput, conversation_id: conversationId }),
			signal: controller.signal
		})

		// 流还没开始就失败（404 会话不存在 / 401 登录过期 / 422 参数不对）。
		// 这些是普通 HTTP 错误，不是 SSE 里的 error 事件。
		if (!resp.ok) {
			let msg = "请求失败(" + resp.status + ")"
			try {
				const j = await resp.json()
				if (j && j.detail) msg = typeof j.detail === "string" ? j.detail : JSON.stringify(j.detail)
			} catch (e) {}
			if (resp.status === 401 || resp.status === 403) {
				try { uni.removeStorageSync("token") } catch (e) {}
				uni.showToast({ title: "登录已过期，请重新登录", icon: "none" })
				setTimeout(() => { uni.reLaunch({ url: "/pages/index/index" }) }, 900)
			}
			throw new Error(msg)
		}

		const reader = resp.body.getReader()
		const decoder = new TextDecoder("utf-8")
		let buffer = ""
		while (true) {
			const chunk = await reader.read()
			if (chunk.done) break
			buffer += decoder.decode(chunk.value, { stream: true })
			// SSE 用一个空行分隔事件，所以按两个换行切；
			// 最后一段可能只收到一半，留给下一次拼接
			const parts = buffer.split("\n\n")
			buffer = parts.pop()
			for (let i = 0; i < parts.length; i++) {
				const evt = parseSseBlock(parts[i])
				if (!evt) continue
				if (evt.event === "stage" && onStage) onStage(evt.data)
				else if (evt.event === "result" && onResult) onResult(evt.data.data)
				else if (evt.event === "error" && onError) onError(new Error(evt.data.text))
			}
		}
	} catch (e) {
		// 用户主动断开（退出页面、点停止）不算错误
		if (e && e.name === "AbortError") return
		if (onError) onError(e)
	}
}
// #endif

// #ifndef H5
const runFallback = async ({ userInput, conversationId, onStage, onResult, onError }) => {
	// 非 H5 端没有流式能力，回落到普通接口，用一句固定文案占住等待期
	if (onStage) onStage({ code: "thinking", text: "正在生成，请稍候…" })
	try {
		const data = await request({
			url: "/chat/", method: "POST", timeout: 120000,
			data: { user_input: userInput, conversation_id: conversationId }
		})
		if (onResult) onResult(data)
	} catch (e) {
		if (onError) onError(e)
	}
}
// #endif

// 发起一次流式对话。返回 controller，页面可以 controller.abort() 主动断开——
// 断开之后后端会把还在跑的 agent 任务取消，不会继续烧模型调用。
export const chatStream = (options) => {
	const controller = new AbortController()
	// #ifdef H5
	runH5Stream(options, controller)
	// #endif
	// #ifndef H5
	runFallback(options)
	// #endif
	return controller
}
export default API
