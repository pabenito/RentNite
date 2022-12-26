function onImageChanged(event) {
    var image = document.getElementById("image");
    image.src = URL.createObjectURL(event.target.files[0]);
}

function createDropin(userIsLoggedIn, paymentToken) {
    if (userIsLoggedIn == "True") {
        const form = document.getElementById("paymentForm");
        const dropinContainer = document.getElementById("dropinContainer");
        const nonce = document.getElementById("nonce");

        braintree.dropin.create(
            {
                authorization: paymentToken,
                container: dropinContainer,
                paypal: {
                    flow: "vault"
                },
                locale: "es_ES"
            },
            (error, dropinInstance) => {
                form.addEventListener("submit", event => {
                    event.preventDefault();

                    dropinInstance.requestPaymentMethod((error, payload) => {
                        nonce.value = payload.nonce;
                        form.submit();
                    });
                });
            }
        );
    }
}

function onDateChanged(from, to) {
    const housePrice = document.getElementById("housePrice").innerText;
    const fromPost = document.getElementById("from");
    const toPost = document.getElementById("to");
    var cost = document.getElementById("cost");
    var costDisplay = document.getElementById("costDisplay");
    var today = new Date();
    today.setHours(0, 0, 0, 0);

    if (today <= from && from < to) {
        var newCost = to.diff(from, 'days') * housePrice;
        newCost = (Math.round(newCost * 100) / 100).toFixed(2);
        cost.value = newCost;
        costDisplay.style.color = "black";
        costDisplay.value = newCost + " €";

        fromPost.value = from.format('YYYY-MM-DD');
        toPost.value = to.format('YYYY-MM-DD');
    } else {
        costDisplay.style.color = "red";
        costDisplay.value = "Fechas incorrectas";
    }
}

function loadDateRangePicker(unavailableDates) {
    var today = new Date();
    today.setHours(0, 0, 0, 0);

    var tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);
    tomorrow.setHours(0, 0, 0, 0);

    $('input[name="date-range"]').daterangepicker(
        {
            locale: {
                format: "DD/MM/YYYY"
            },
            isInvalidDate: function(date) { 
                var today = new Date();
                today.setHours(0, 0, 0, 0);

                if (date < today) {
                    return true;
                }

                var i = 0;
                var isValid = true;
                while (i < unavailableDates.length && isValid) {
                    var from = new Date(unavailableDates[i]["from"]);
                    from.setHours(0, 0, 0, 0);

                    var to = new Date(unavailableDates[i]["to"]);
                    to.setHours(0, 0, 0, 0);

                    isValid = date < from || date > to;

                    i++;
                }

                return !isValid;
             },
             startDate: today,
             endDate: tomorrow,
             autoApply: true
        }, 
        function(from, to, label) {
            from = moment(from.format('YYYY-MM-DD'));
            to = moment(to.format('YYYY-MM-DD'));
            onDateChanged(from, to);
        }
    );
}

function loadHouseDetails(userIsLoggedIn, paymentToken, unavailableDates) {
    createDropin(userIsLoggedIn, paymentToken);
    loadDateRangePicker(unavailableDates);
}