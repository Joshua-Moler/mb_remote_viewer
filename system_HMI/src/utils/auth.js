import savePermissions from '../usePermissions'

async function Login(email, password) {

    if (!email.length || !password.length) {
        throw new Error('Email or Password was not Provided')
    }

    const formData = new FormData()

    formData.append('username', email)
    formData.append('password', password)


    const request = new Request('/api/token', {
        method: 'POST',
        body: formData
    })

    const response = await fetch(request)

    if (response.status === 500) {
        throw new Error('Internal Server Error')
    }

    const data = await response.json()

    if (response.status > 400 && response.status < 500) {
        if (data.detail) {
            throw data.detail
        }
        throw data
    }


    if ('permissions' in data) {
        savePermissions(data['permissions'])
    }

    return data
}

async function CreateAccount(email, password, passwordConfirm) {
    if (!email.length) {
        throw new Error('Email was not Provided')
    }
    if (!password.length) {
        throw new Error('Password was not Provided')
    }
    if (!passwordConfirm) {
        throw new Error('Password Confirmation was not Provided')
    }
    if (password !== passwordConfirm) {
        throw new Error('Passwords do not Match')
    }

    const formData = new FormData

    formData.append('username', email)
    formData.append('password', password)

    const request = new Request('/api/signup', {
        method: 'POST',
        body: formData
    })

    const response = await fetch(request)

    if (response.status === 500) {
        throw new Error('Internal Server Error')
    }

    const data = await response.json()
    if (response.status > 400 && response.status < 500) {
        if (data.detail) {
            throw data.detail
        }
        throw data
    }

    return data
}


async function Logout() {
    savePermissions(null)
    const request = new Request('/api/signup', {
        method: 'POST',
    })
    const response = await fetch(request)
    const data = await response.json()
    return data
}

export { Login, CreateAccount, Logout }