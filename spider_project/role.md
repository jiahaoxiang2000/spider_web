# Role Management

The `web.antgst.com` role has an issue where unauthorized users can modify roles.

## Modify a Normal User's Role

### 1. Get the User ID by Username

First, retrieve the username using the `/sys/user/getUserListByName` endpoint.

- **Request**: `GET` with parameter `userName`.
- **Response** (`application/json`):

    ```json
    [
        {
            "id": "d2eb78d61bec605211c2df41160efb56",
            "userName": "dev_LCX"
        }
    ]
    ```

### 2. Get the Role ID by User ID

The role ID is related to the user ID. Retrieve the role ID using the `/sys/user/queryUserRole` endpoint.

- **Request**: `GET` with parameter `userid`.
- **Response** (`application/json`):

    ```json
    {
        "success": true,
        "message": "操作成功！",
        "code": 0,
        "result": [
            "082678e5d9270824353a223a6727e009"
        ],
        "timestamp": 1729644331828
    }
    ```

### 3. Change the Role ID

To change the role ID, follow these steps:

1. **Delete the Current Role**:

    Use the `/sys/user/deleteUserRole` endpoint to remove the current role from the user.

    - **Request**: `DELETE` with parameters `roleId` and `userId`.
    - **Response** (`application/json`):

        ```json
        {
            "success": true,
            "message": "删除成功!",
            "code": 200,
            "result": null,
            "timestamp": 1729644302546
        }
        ```

2. **Add the New Role**:

    Use the `/sys/user/addSysUserRole` endpoint to assign the new role to the user.

    - **Request**: `POST` body.
    - **POST Body** (`application/json`):
  
        ```json
        {
            "roleId": "082678e5d9270824353a223a6727e009",
            "userIdList": [
                "58d1e992a5e0bb5ad99538233bc3026a"
            ]
        }
        ```

    - **Response** (`application/json`):

       ```json
        {
            "success": true,
            "message": "添加成功!",
            "code": 0,
            "result": null,
            "timestamp": 1729644328305
        }
        ```

### Note

1. When reverting the role, deleting the original role from the user will cause the role to be lost. To prevent this, store the original `roleId` and `username` in the Django model using the SQLite3 database. When reverting, retrieve the original `roleId` and `username` to reassign the role to the user.
2. the all request need add the header field `X-Access-Token`.
