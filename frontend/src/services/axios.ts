import axios from 'axios'

const baseUri = 'http://localhost:8000/api/v1'
const HTTP = axios.create({
    baseURL:baseUri,
    timeout:1000,
    withCredentials:true

})

HTTP.interceptors.request.use(config => {
    if(config.baseURL === baseUri && !config.headers.Authorization) {
        const token = localStorage.getItem('token')
        console.log(token,'did it come like that')
        if(token) {
            config.headers.Authorization = `Bearer ${token}`
        }

        return config
    }
},
error => Promise.reject(error)
)

HTTP.interceptors.response.use(res => {
    if(res.headers.hasAuthorization()) {
        localStorage.setItem('token',res.headers.getAuthorization())
        console.log('res interceptors running',res.headers.getAuthorization())
        
    }

    return res


},
err => Promise.reject(err)
)


export {HTTP}


