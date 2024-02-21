
// Get the canvas element and 2D context
const canvas = document.getElementById('myCanvas');
const context = canvas.getContext('2d');
context.fillStyle = "#ffffff"; // or "white" for a simpler form
context.fillRect(0, 0, canvas.width, canvas.height);
// Variable to track mouse coordinates
let mouseX, mouseY;

// Variable to track whether the mouse button is currently held down
let isMouseDown = false;

// Variable to store previous mouse coordinates
let prevMouseX, prevMouseY;

// Data array to store timestamped coordinates
let data = [];

// Event listener for mouse down
canvas.addEventListener('mousedown', function(event) {
    // Check if it's a left click (button value 0)
    if (event.button === 0) {
        isMouseDown = true;
        updateMouseCoordinates(event);
    }
});

// Event listener for mouse up
canvas.addEventListener('mouseup', function() {
    isMouseDown = false;
    // Reset previous coordinates when the mouse button is released
    prevMouseX = undefined;
    prevMouseY = undefined;
});

// Event listener for mouse movement
canvas.addEventListener('mousemove', function(event) {
    if (isMouseDown) {
        updateMouseCoordinates(event);

        // Draw a line from the previous point to the current point
        if (prevMouseX !== undefined && prevMouseY !== undefined) {
            context.beginPath();
            context.moveTo(prevMouseX, prevMouseY);
            context.lineTo(mouseX, mouseY);
            context.strokeStyle = 'blue';
            context.lineWidth = 2;
            context.stroke();

            // Log coordinates and timestamp
                
            const coordinates = { x: mouseX, y: mouseY };
            data.push([coordinates]);
           

         //   console.log(`Mouse Coordinates at ${timestamp}: (${mouseX}, ${mouseY})`);
        }

        // Store current coordinates as the previous coordinates for the next movement
        prevMouseX = mouseX;
        prevMouseY = mouseY;
    }
});

// Function to update mouse coordinates
function updateMouseCoordinates(event) {
    const rect = canvas.getBoundingClientRect();
    mouseX= event.clientX - rect.left;
    mouseY= event.clientY - rect.top;
   
}

// Function to create and download CSV file
function downloadCSV() {
    JSON.stringify(data);

        // Check if data is an array of arrays
        if (Array.isArray(data) && data.length > 0 && Array.isArray(data[0]) && data[0].length === 1) {
            // Extract the single element from each inner array
            const extractedData = data.map(entry => entry[0]);
    
            const csvContent = "data:text/csv;charset=utf-8," +
                extractedData.map(entry => [entry.x, entry.y].join(','));
    
            const encodedUri = encodeURI(csvContent);
            const link = document.createElement("a");
            link.setAttribute("href", encodedUri);
            link.setAttribute("download", "mouse_coordinates.csv");
            document.body.appendChild(link);
            link.click();
        } else {
            console.error("Invalid data format. Please check the structure of the 'data' array.");
        }
    }
    


// Event listener for download button
document.getElementById('downloadBtn').addEventListener('click', () => {
    
    var num = "02";
    canvas.toBlob((blob) => {
        saveBlob(blob, `deepak_${num}.png`);
      });
   
    const saveBlob = (function() {
      const a = document.createElement('a');
      document.body.appendChild(a);
      a.style.display = 'none';
      return function saveData(blob, fileName) {
         const url = window.URL.createObjectURL(blob);
         a.href = url;
         a.download = fileName;
         a.click();
      };
    }());
   // console.log(data);
    downloadCSV();
});
