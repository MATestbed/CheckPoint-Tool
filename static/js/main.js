let selectedImages = [];
let currentFolderPath = "";
let currentFolderItem;  // 定义一个变量来存储当前被点击的 folderItem

document.addEventListener('DOMContentLoaded', function() {
    const pathForm = document.getElementById('pathForm');
    const folderList = document.getElementById('folderList');
    const imageCarousel = document.getElementById('imageCarousel');

    // Handle the form submission
    pathForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const path = document.getElementById('pathInput').value;
        
        // Send a POST request to the Flask backend to get the list of folders
        fetch('/get_folders', {
            method: 'POST',
            body: new URLSearchParams({ 'path': path }),
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        })
        .then(response => response.json())
        .then(folders => {
            folderList.innerHTML = '';
            folders.forEach(folder => {

                const folderItem = document.createElement('div');
                folderItem.className = 'folderItem';  // 设置 class 为 folderItem
                folderItem.textContent = folder;
                // folderItem.innerText =  folder;
                folderItem.addEventListener('click', function() {

                    // 更新 currentFolderItem 变量
                    currentFolderItem = folderItem;
                    // Reset selectedImages for each folder click
                    selectedImages = [];
                    currentFolderPath = path + "/" + folder;

                    // When a folder is clicked, send a POST request to get the images in that folder
                    fetch('/get_images', {
                        method: 'POST',
                        body: new URLSearchParams({ 'path': path +"/" + folder }),
                        headers: {
                            'Content-Type': 'application/x-www-form-urlencoded'
                        }
                    })
                    .then(response => response.json())
                    .then(images => {

                        imageCarousel.innerHTML = '';
                        images.forEach(image => {

                            const imgDiv = document.createElement('div');
                            imgDiv.className = 'item'; // 给图片和文本框的容器添加类名
                            
                            const img = document.createElement('img');
                            img.src = '/image?path=' + image;
                            
                            const textarea = document.createElement('textarea');
                            textarea.placeholder = 'Enter annotation here...';
                            textarea.className = 'image-annotation'; // 给文本框添加类名


                            // Load the existing annotation for the image, if it exists
                            const annotationPath = currentFolderPath + '/' + image.split('/').pop() + '.text';
                            fetch('/get_annotation', {
                                method: 'POST',
                                body: new URLSearchParams({ 'annotation_path': annotationPath }),
                                headers: {
                                    'Content-Type': 'application/x-www-form-urlencoded'
                                }
                            })
                            .then(response => {
                                if (response.status === 204) {
                                    return ''; // 如果服务器返回204 No Content，返回空字符串
                                }
                                return response.text();
                            })
                            .then(annotation => {
                                textarea.value = annotation; // Set the textbox content, it will be empty if no annotation was fetched
                            })
                            // .then(annotation => {
                            //     if (annotation) {
                            //         textarea.value = annotation; // Set the textbox content
                            //     }
                            // })
                            .catch(error => {
                                console.error('Error fetching annotation:', error);
                            });
                            
                            imgDiv.appendChild(img);
                            imgDiv.appendChild(textarea);
                            imageCarousel.appendChild(imgDiv);

                            // @
                            // const imgDiv = document.createElement('div');
                            // const img = document.createElement('img');
                            // img.src = '/image?path=' + image;
                            // imgDiv.appendChild(img);
                            // imageCarousel.appendChild(imgDiv);

                            imgDiv.addEventListener('click', function() {
                                 imagePath = image;
                                 imagePath = imagePath.split("/").pop();
                                if (imgDiv.classList.contains('selected-image')) {
                                    imgDiv.classList.remove('selected-image');
                                    selectedImages = selectedImages.filter(img => img !== imagePath);
                                } else {
                                    imgDiv.classList.add('selected-image');
                                    selectedImages.push(imagePath);
                                }
                            });
                        });

                        // 如果 imageCarousel 已经被初始化为轮播，则先销毁它
                        if ($(imageCarousel).hasClass('owl-loaded')) {
                            $(imageCarousel).owlCarousel('destroy');
                        }
                    
                        // 初始化 Owl Carousel
                        $(imageCarousel).owlCarousel({
                            loop: false,
                            margin: 10,
                            items: 4,
                            // nav: true,
                            // navText: ["<i class='fa fa-chevron-left'></i>", "<i class='fa fa-chevron-right'></i>"]
                        });
                        
                        // 使用jquery-mousewheel插件标准化鼠标滚轮事件
                        $(imageCarousel).on('mousewheel', '.owl-stage', function (e) {
                            if (e.deltaY > 0) {
                                $(imageCarousel).trigger('prev.owl');
                                // $(imageCarousel).trigger('prev.owl.carousel');
                            } else {
                                // $(imageCarousel).trigger('next.owl.carousel');
                                $(imageCarousel).trigger('next.owl');
                            }
                            e.preventDefault();
                        });


                    });

                    // 新增的部分：从后端请求 instruction.txt 的内容
                    fetch('/get_instruction', {
                        method: 'POST',
                        body: new URLSearchParams({ 'folder_path': path + "/" + folder }),
                        headers: {
                            'Content-Type': 'application/x-www-form-urlencoded'
                        }
                    })
                    .then(response => response.text())  // 假设服务器返回纯文本
                    .then(instruction => {
                        const instructionDiv = document.getElementById('instructionText');
                        instructionDiv.textContent = instruction;  // 设置文本内容
                    })
                    .catch(error => {
                        console.error('Error fetching instruction:', error);
                    });
                    
                });
                folderList.appendChild(folderItem);
            });
        })
        .catch(error => {
            console.error('Error fetching folders:', error);
        });
    });
});

// // @
// document.getElementById('annotateBtn').addEventListener('click', function() {
//     fetch('/save_annotations', {
//         method: 'POST',
//         body: JSON.stringify({
//             'selectedImages': selectedImages,
//             'currentFolderPath': currentFolderPath
//         }),
//         headers: {
//             'Content-Type': 'application/json'
//         }
//     })
    // .then(response => response.json())
    // .then(data => {
    //     console.log(data.message);
    //     // 如果标注成功，为 currentFolderItem 添加 annotated 类
    //     if (currentFolderItem) {
    //         currentFolderItem.classList.add('annotated');
    //     }
    // })
    // .catch(error => {
    //     console.error('Error saving annotations:', error);
    // });
// });


document.getElementById('annotateBtn').addEventListener('click', function() {
    const annotations = document.querySelectorAll('.image-annotation');
    const annotationsData = Array.from(annotations).map(textarea => textarea.value);

    fetch('/save_annotations', {
        method: 'POST',
        body: JSON.stringify({
            'selectedImages': selectedImages,
            'annotations': annotationsData,
            'currentFolderPath': currentFolderPath
        }),
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        console.log(data.message);
        if (data.error) {
            console.error('Error saving annotations:', data.error);
        } else {
            // Handle success
            if (currentFolderItem) {
                currentFolderItem.classList.add('annotated');
            }
        }
    })
    .catch(error => {
        console.error('Error saving annotations:', error);
    });
});



// let selectedImages = [];
// let currentFolderPath = "";

// document.addEventListener('DOMContentLoaded', function() {
//     const pathForm = document.getElementById('pathForm');
//     const folderList = document.getElementById('folderList');
//     const imageCarousel = document.getElementById('imageCarousel');

//     // Handle the form submission
//     pathForm.addEventListener('submit', function(e) {
//         e.preventDefault();
//         const path = document.getElementById('pathInput').value;
        
//         fetch('/get_folders', {
//             method: 'POST',
//             body: new URLSearchParams({ 'path': path }),
//             headers: {
//                 'Content-Type': 'application/x-www-form-urlencoded'
//             }
//         })
//         .then(response => response.json())
//         .then(folders => {
//             folderList.innerHTML = '';
//             folders.forEach(folder => {
//                 const folderItem = document.createElement('div');
//                 folderItem.innerText = folder;
//                 folderItem.addEventListener('click', function() {
//                     // Reset selectedImages for each folder click
//                     selectedImages = [];
//                     currentFolderPath = path + "/" + folder;

//                     fetch('/get_images', {
//                         method: 'POST',
//                         body: new URLSearchParams({ 'path': currentFolderPath }),
//                         headers: {
//                             'Content-Type': 'application/x-www-form-urlencoded'
//                         }
//                     })
//                     .then(response => response.json())
//                     .then(images => {
//                         imageCarousel.innerHTML = '';
//                         images.forEach(image => {
//                             const imgDiv = document.createElement('div');
//                             const img = document.createElement('img');
//                             img.src = '/image?path=' + image;
//                             imgDiv.appendChild(img);
//                             imageCarousel.appendChild(imgDiv);

//                             imgDiv.addEventListener('click', function() {
//                                 const imagePath = image;
//                                 if (imgDiv.classList.contains('selected-image')) {
//                                     imgDiv.classList.remove('selected-image');
//                                     selectedImages = selectedImages.filter(img => img !== imagePath);
//                                 } else {
//                                     imgDiv.classList.add('selected-image');
//                                     selectedImages.push(imagePath);
//                                 }
//                             });
//                         });

//                         if ($(imageCarousel).hasClass('owl-loaded')) {
//                             $(imageCarousel).owlCarousel('destroy');
//                         }

//                         $(imageCarousel).owlCarousel({
//                             loop: false,
//                             margin: 10,
//                             items: 3
//                         });

//                         $(imageCarousel).on('mousewheel', '.owl-stage', function (e) {
//                             if (e.deltaY > 0) {
//                                 $(imageCarousel).trigger('prev.owl.carousel');
//                             } else {
//                                 $(imageCarousel).trigger('next.owl.carousel');
//                             }
//                             e.preventDefault();
//                         });

//                     });
//                 });
//                 folderList.appendChild(folderItem);
//             });
//         })
//         .catch(error => {
//             console.error('Error fetching folders:', error);
//         });
//     });

//     document.getElementById('annotateBtn').addEventListener('click', function() {
//         fetch('/save_annotations', {
//             method: 'POST',
//             body: JSON.stringify({
//                 'selectedImages': selectedImages,
//                 'currentFolderPath': currentFolderPath
//             }),
//             headers: {
//                 'Content-Type': 'application/json'
//             }
//         })
//         .then(response => response.json())
//         .then(data => {
//             console.log(data.message);
//         })
//         .catch(error => {
//             console.error('Error saving annotations:', error);
//         });
//     });
// });
