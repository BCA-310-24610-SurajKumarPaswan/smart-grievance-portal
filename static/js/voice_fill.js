function startVoiceFill() {

    alert("Voice working");

    let SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
        alert("Use Chrome browser");
        return;
    }

    let recognition = new SpeechRecognition();
    recognition.lang = "en-IN";
    recognition.start();

    recognition.onresult = function (event) {
        let text = event.results[0][0].transcript;

        document.getElementById("description").value = text;
        document.getElementById("title").value = text.substring(0, 40);
    };
}