import { useState } from 'react';

export default function useToken() {

    const getToken = () => {
        const tokenString = localStorage.getItem('token');
        const userToken = JSON.parse(tokenString);
        return userToken?.token;
    };
    const [token, setToken] = useState(getToken());

    const saveToken = userToken => {
        if (userToken) {
            localStorage.setItem('token', JSON.stringify(userToken));
            setToken(userToken.token);
        }
        else {
            localStorage.removeItem('token')
            setToken(undefined)
        }
    }

    return {
        setToken: saveToken,
        token
    }
}