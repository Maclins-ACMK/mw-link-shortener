const API = "https://mw-link-shortener.onrender.com"

let token = ""

async function register() {

let email = document.getElementById("regEmail").value
let password = document.getElementById("regPass").value

await fetch(API + "/register",{
method:"POST",
headers:{"Content-Type":"application/json"},
body:JSON.stringify({email,password})
})

alert("Registered successfully")

}

async function login(){

let email = document.getElementById("logEmail").value
let password = document.getElementById("logPass").value

let form = new URLSearchParams()
form.append("username",email)
form.append("password",password)

let res = await fetch(API + "/login",{
method:"POST",
headers:{"Content-Type":"application/x-www-form-urlencoded"},
body:form
})

let data = await res.json()

token = data.access_token

alert("Login successful")

}

async function createLink(){

let url = document.getElementById("longUrl").value

let res = await fetch(API + "/links",{
method:"POST",
headers:{
"Content-Type":"application/json",
"Authorization":"Bearer "+token
},
body:JSON.stringify({original_url:url})
})

let data = await res.json()
console.log(data)

document.getElementById("result").innerHTML =
`<a href="${data.short_url}" target="_blank">${data.short_url}</a>`

}