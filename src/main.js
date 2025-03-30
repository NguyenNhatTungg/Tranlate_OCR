sendFile = function(file, path) {

    var item = document.createElement('li');
    var formData = new FormData();
    var request = new XMLHttpRequest();

    request.responseType = 'text';

    // HTTP onload handler
    request.onload = function() {
        if (request.readyState === request.DONE) {
            if (request.status === 200) {
                console.log(request.responseText);

                // Add file name to list
                listing.innerHTML = request.responseText + " (" + counter + " of " + total + " ) ";

                // Show percentage
                box.innerHTML = Math.min(counter / total * 100, 100).toFixed(2) + "%";

                // Show progress bar
                elem.innerHTML = Math.round(counter / total * 100, 100) + "%";
                elem.style.width = Math.round(counter / total * 100) + "%";

                // Render image if file is an image
                if (file.type.startsWith('image/')) {
                    const img = document.createElement('img');
                    img.src = URL.createObjectURL(file);
                    img.style.maxWidth = '200px';
                    img.style.margin = '10px';
                    listing.appendChild(img);
                }

                // Increment counter
                counter = counter + 1;
            }
            if (counter >= total) {
                listing.innerHTML = "Uploading " + total + " file(s) is done!";
                loader.style.display = "none";
                loader.style.visibility = "hidden";
            }
        }
    };

    // Set post variables 
    formData.set('file', file); // One object file
    formData.set('path', path); // String of local file's path 

    // Do request
    // request.open("POST", 'process.php');
    request.send(formData);

};


