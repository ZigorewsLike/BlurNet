
new Vue({        
    el: '#app',
    data(){ 
        return{
            message: ' Vue is connected! ',
            debug: false,
            blur_value: 0,
            new_img: {
                filter: 'blur(0px)',
                backgroundImage: "url(static/source/1.jpg)",
            },
            selctedFile: null,
            base64Img: new Image(),
            imgDir:{
                backgroundImage: "url(static/source/1.jpg)",
            },
            keysession: 0,
            blur_proc: false,
            blur_img: '',
            uploaded: false,
        }
    },
    created: function(){
        this.keysession = Math.floor(Math.random() * (1000000000000000 - 1 + 1)) + 1;
        console.log(this.keysession);
        this.base64Img.src = 'url(static/source/1.jpg)';
    },
    methods: {
        onBlurChange(e){
            this.blur_value = e.target.value;
            this.new_img.filter = 'blur(' + this.blur_value / 100 + 'px)';
            this.new_img.backgroundImage = 'url(' + this.base64Img.src + ')'
        },
        uploadImage(event){
            console.log(event);
            this.selctedFile = event.target.files[0];
            this.base64Img.src = URL.createObjectURL(this.selctedFile);
            this.imgDir.backgroundImage = 'url(' + this.base64Img.src + ')';
            this.new_img.backgroundImage = 'url(' + this.base64Img.src + ')';

            console.log(this.base64Img)
            this.uploaded = true;
        },
        async submitdata(api_name){
            this.blur_proc = true;
            var pojiloygibon267 = Cookies.get('csrftoken');
            console.log(pojiloygibon267);
            try{
                var fd = new FormData();
                fd.append('keysession', this.keysession);
                fd.append('img', this.selctedFile);
                fd.append('title', this.selctedFile.name);
                fd.append('blurInt', this.blur_value);
                fd.append('outputPath', '0');
            
            
                var opt_post = false;
                await axios({
                    method : "post",
                    url : "/api/" + api_name + "/",
                    data : fd,
                    headers : {"X-CSRFToken" : pojiloygibon267, 'Content-Type': 'multipart/form-data'}
                }).then(function(resp){
                    opt_post = true;
                }).catch(function(error){
                    console.log(error)
                    this.blur_proc = false;
                });
                this.new_img.filter = 'blur(0px)';

                if (opt_post){
                    await axios({
                        method : "get",
                        url : "/api/" + api_name + "/",
                        headers : {"X-CSRFToken" : pojiloygibon267 }
                    }).then(response => {
                        var data = response.data;
                        for(const el in data){
                            if (data[el].keysession == this.keysession && data[el].blurInt == this.blur_value && data[el].title == this.selctedFile.name){
                                //console.log(data[el].outputPath)
                                this.new_img.backgroundImage = 'url(' + data[el].outputPath + ')';
                                this.blur_img = (data[el].outputPath).substring(19);
                                console.log('img = ', this.blur_img);
                                break;
                            }
                        }
                    }).catch(function(error){
                        console.log(error);
                        this.blur_proc = false;
                    }); 
                }
                window.open('/blur'+this.blur_img, "_blank")
                this.blur_proc = false;
            }catch(error){
                alert("Не удолось сформировать изображение");
                this.blur_proc = false;
            }

        },
        
    }
})