    function createLauncherPanel() {
        var div = document.createElement("div");
        div.setAttribute("class", "launcher-panel");
        div.classList.add("hidden");
        div.appendChild(createLauncherLink(div));

        document.getElementsByTagName("body")[0].appendChild(div);

        return div;
    }

    function createLauncherLink(container) {
        var link = document.createElement("link");

        link.setAttribute("rel", "import");
        link.setAttribute("href", "{{url}}");

        link.onload = function () {
            container.appendChild(link.import.querySelector('.launcher-main-container'));
        };

        return link;
    }

    createLauncherPanel();