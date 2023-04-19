import { useState } from 'react';

export default function usePermissions() {

    const getPermissions = () => {
        const permissionsString = localStorage.getItem('permissions');
        const userPermissions = JSON.parse(permissionsString);
        return userPermissions?.permissions;
    };
    const [permissions, setPermissions] = useState(getPermissions());

    const savePermissions = userPermissions => {
        if (userPermissions) {
            localStorage.setItem('permissions', JSON.stringify(userPermissions));
            setPermissions(userPermissions.token);
        }
        else {
            localStorage.removeItem('permissions')
            setPermissions(undefined)
        }
    }

    return {
        setPermissions: savePermissions,
        permissions
    }
}