// =====================================
// DX FRAGRANCE
// Main JavaScript
// =====================================

document.addEventListener("DOMContentLoaded", function () {

    console.log("DX Fragrance website loaded successfully.");


    // =========================================================
    // ELEMENTS
    // =========================================================

    const searchInput =
        document.getElementById("navbarMainSearch");

    const suggestions =
        document.getElementById("navbarSearchSuggestions");

    const micButton =
        document.getElementById("navbarMicButton");


    // =========================================================
    // NORMAL SEARCH
    // =========================================================

    if (searchInput && suggestions) {

        let searchTimer;


        searchInput.addEventListener(
            "input",
            function () {

                const value =
                    searchInput.value.trim();

                clearTimeout(searchTimer);


                if (!value) {

                    suggestions.innerHTML = "";

                    suggestions.classList.remove(
                        "active"
                    );

                    return;
                }


                searchTimer = setTimeout(
                    function () {

                        fetch(
                            "/products/search-suggestions?q=" +
                            encodeURIComponent(value)
                        )

                        .then(function (response) {

                            if (!response.ok) {

                                throw new Error(
                                    "Search request failed"
                                );

                            }

                            return response.json();

                        })

                        .then(function (products) {

                            suggestions.innerHTML = "";


                            if (
                                !products ||
                                products.length === 0
                            ) {

                                suggestions.innerHTML = `
                                    <div class="search-no-result">
                                        No fragrance found
                                    </div>
                                `;

                                suggestions.classList.add(
                                    "active"
                                );

                                return;
                            }


                            products.forEach(
                                function (product) {

                                    const item =
                                        document.createElement("a");


                                    item.href =
                                        "/product/" +
                                        product.id;


                                    item.className =
                                        "search-suggestion";


                                    let imageHTML = "";


                                    if (product.image) {

                                        imageHTML = `
                                            <img
                                                src="/static/uploads/products/${product.image}"
                                                class="search-suggestion-image"
                                                alt="${product.name}"
                                            >
                                        `;

                                    } else {

                                        imageHTML = `
                                            <div
                                                class="search-suggestion-image"
                                            >
                                                DX
                                            </div>
                                        `;

                                    }


                                    item.innerHTML = `

                                        ${imageHTML}

                                        <span
                                            class="search-suggestion-info"
                                        >

                                            <span
                                                class="search-suggestion-name"
                                            >
                                                ${product.name}
                                            </span>

                                            <span
                                                class="search-suggestion-category"
                                            >
                                                ${
                                                    product.category ||
                                                    "Premium Fragrance"
                                                }
                                            </span>

                                        </span>

                                        <span
                                            class="search-suggestion-price"
                                        >
                                            ₹${product.price}
                                        </span>

                                    `;


                                    suggestions.appendChild(
                                        item
                                    );

                                }
                            );


                            suggestions.classList.add(
                                "active"
                            );

                        })

                        .catch(function (error) {

                            console.error(
                                "Search error:",
                                error
                            );

                            suggestions.innerHTML = "";

                            suggestions.classList.remove(
                                "active"
                            );

                        });

                    },
                    250
                );

            }
        );


        // =====================================================
        // ENTER TO SEARCH
        // =====================================================

        searchInput.addEventListener(
            "keydown",
            function (event) {

                if (event.key === "Enter") {

                    event.preventDefault();


                    const value =
                        searchInput.value.trim();


                    if (value) {

                        window.location.href =
                            "/products?search=" +
                            encodeURIComponent(value);

                    }

                }

            }
        );


        // =====================================================
        // CLOSE SUGGESTIONS
        // =====================================================

        document.addEventListener(
            "click",
            function (event) {

                const wrapper =
                    document.querySelector(
                        ".navbar-search-wrapper"
                    );


                if (
                    wrapper &&
                    !wrapper.contains(
                        event.target
                    )
                ) {

                    suggestions.classList.remove(
                        "active"
                    );

                }

            }
        );

    }



    // =========================================================
    // 🎙️ VOICE SEARCH
    // =========================================================

    if (micButton && searchInput) {

        const SpeechRecognition =
            window.SpeechRecognition ||
            window.webkitSpeechRecognition;


        // =====================================================
        // CHECK BROWSER SUPPORT
        // =====================================================

        if (!SpeechRecognition) {

            console.error(
                "Speech Recognition is not supported."
            );


            micButton.addEventListener(
                "click",
                function () {

                    alert(
                        "Voice search is not supported in this browser. Please use Google Chrome."
                    );

                }
            );


        } else {

            const recognition =
                new SpeechRecognition();


            // =================================================
            // VOICE SETTINGS
            // =================================================

            // English India works better for Hinglish
            recognition.lang = "en-IN";

            recognition.continuous = false;

            recognition.interimResults = true;

            recognition.maxAlternatives = 3;


            let isListening = false;


            // =================================================
            // MIC CLICK
            // =================================================

            micButton.addEventListener(
                "click",
                function (event) {

                    event.preventDefault();


                    if (isListening) {

                        recognition.stop();

                        return;

                    }


                    try {

                        recognition.start();

                    }

                    catch (error) {

                        console.error(
                            "Speech start error:",
                            error
                        );

                    }

                }
            );


            // =================================================
            // START LISTENING
            // =================================================

            recognition.onstart =
                function () {

                    isListening = true;


                    micButton.classList.add(
                        "listening"
                    );


                    micButton.innerHTML =
                        "🎙️";


                    micButton.title =
                        "Listening... Speak now";


                    searchInput.placeholder =
                        "Listening... speak now";


                    searchInput.focus();


                    console.log(
                        "🎙️ Listening started..."
                    );

                };


            // =================================================
            // SPEECH RESULT
            // =================================================

            recognition.onresult =
                function (event) {

                    let transcript = "";


                    for (
                        let i = event.resultIndex;
                        i < event.results.length;
                        i++
                    ) {

                        transcript +=
                            event.results[i][0]
                                .transcript;

                    }


                    transcript =
                        transcript.trim();


                    console.log(
                        "🎙️ Voice result:",
                        transcript
                    );


                    if (transcript) {

                        searchInput.value =
                            transcript;


                        searchInput.focus();

                    }


                    // -----------------------------------------
                    // FINAL RESULT
                    // -----------------------------------------

                    const lastResult =
                        event.results[
                            event.results.length - 1
                        ];


                    if (
                        lastResult &&
                        lastResult.isFinal
                    ) {

                        searchInput.dispatchEvent(
                            new Event("input")
                        );

                    }

                };


            // =================================================
            // NO MATCH
            // =================================================

            recognition.onnomatch =
                function () {

                    console.log(
                        "No matching speech found."
                    );

                };


            // =================================================
            // ERROR
            // =================================================

            recognition.onerror =
                function (event) {

                    console.error(
                        "🎙️ Voice error:",
                        event.error
                    );


                    isListening = false;


                    micButton.classList.remove(
                        "listening"
                    );


                    micButton.innerHTML =
                        "🎙️";


                    micButton.title =
                        "Voice Search";


                    searchInput.placeholder =
                        "Search for fragrances, brands and more";


                    // Don't show annoying popup
                    if (
                        event.error === "no-speech"
                    ) {

                        console.log(
                            "No speech detected."
                        );

                        return;

                    }


                    if (
                        event.error === "not-allowed"
                    ) {

                        alert(
                            "Microphone permission blocked hai. Chrome mein microphone Allow karo."
                        );

                        return;

                    }


                    if (
                        event.error === "audio-capture"
                    ) {

                        alert(
                            "Microphone detect nahi ho raha."
                        );

                        return;

                    }


                    if (
                        event.error === "network"
                    ) {

                        alert(
                            "Browser ka voice recognition service available nahi hai."
                        );

                        return;

                    }

                };


            // =================================================
            // RECOGNITION END
            // =================================================

            recognition.onend =
                function () {

                    isListening = false;


                    micButton.classList.remove(
                        "listening"
                    );


                    micButton.innerHTML =
                        "🎙️";


                    micButton.title =
                        "Voice Search";


                    searchInput.placeholder =
                        "Search for fragrances, brands and more";


                    console.log(
                        "🎙️ Listening ended."
                    );

                };

        }

    }



    // =========================================================
    // MOBILE MENU
    // =========================================================

    const mobileMenu =
        document.querySelector(
            ".mobile-menu"
        );


    const navMenu =
        document.querySelector(
            ".nav-menu"
        );


    if (
        mobileMenu &&
        navMenu
    ) {

        mobileMenu.addEventListener(
            "click",
            function () {

                navMenu.classList.toggle(
                    "mobile-open"
                );

            }
        );

    }

});