
        function showPassword(id) {
            let ele = document.getElementById(id)
            if (ele.type === "password")
                ele.type = "text";
            else
                ele.type = "password";
        }
