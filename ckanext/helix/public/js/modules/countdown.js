
//import countdown from 'countdown'

this.ckan.module('countdown', {

    initialize: function () {
        console.log('In module initialize');
        var $el = $(this.el)
        if ($.fn.countdown) {
            console.log('Countdown imported successfuly');
        }
        else{
            console.log('Countdown not imported');
        }
        let climateClock = {
            startDateUTC: [2018, 0, 1, 0, 0, 0],
            startDateCO2Budget: 4.2e+11,
            tonsPerSecond: 1330.899688189216,
            initialized: false,

            init() {
                console.log('In init');
                if (!$('.climate-clock').length) { return; }
                //this.fullScreen();
                this.initCountDown();
                this.calcLabelSize();
            },

            fullScreen() {
                $('.home .climate-clock').click((e) => {
                    $(e.currentTarget).toggleClass('fullscreen');
                    $('html').toggleClass('overflow-hidden');
                });
            },

            calcLabelSize() {
                if ($('.climate-clock').length && $('.climate-clock__data__item__value').length) {
                    let max_width = 0;
                    $('.climate-clock__data__item__value').each((index, row) => {
                        $(row).css({ 'min-width': `0px` })
                        const width = $(row).width();
                        $(row).css({ 'min-width': `${width}px` })
                    });
                    $('.climate-clock__data__item__label').each((index, row) => {
                        const width = $(row).width();
                        if (width > max_width) {
                            max_width = width;
                        }
                    });
                    $('.climate-clock__data__item__label').css({ width: `${max_width}px`, height: '30px' })
                }
            },

            initCountDown() {
                if (!$('.climate-clock').length) { return; }
                let count_down = countdown(this.deadline(), new Date(), countdown.YEARS | countdown.DAYS | countdown.HOURS | countdown.MINUTES | countdown.SECONDS)
                this.updateCounter(count_down);
                if (!this.initialized) {
                    $('.climate-clock').css('opacity', '1');
                    this.initialized = true;
                }
                setInterval(() => {
                    let count_down =countdown(this.deadline(), new Date(), countdown.YEARS | countdown.DAYS | countdown.HOURS | countdown.MINUTES | countdown.SECONDS)
                    this.updateCounter(count_down);
                }, 997);
            },

            updateCounter(count_down) {
                if (!count_down) return;
                $('#climateYear').html(count_down.years < 10 ? `0${count_down.years}` : count_down.years)
                $('#climateDays').html(count_down.days < 10 ? `0${count_down.days}` : count_down.days)
                $('#climateHours').html(count_down.hours < 10 ? `0${count_down.hours}` : count_down.hours)
                $('#climateMinutes').html(count_down.minutes < 10 ? `0${count_down.minutes}` : count_down.minutes)
                $('#climateSeconds').html(count_down.seconds < 10 ? `0${count_down.seconds}` : count_down.seconds)
            },

            deadline() {
                let msRemainingAtStartDate = (this.startDateCO2Budget / this.tonsPerSecond * 1000)
                return new Date(this.startDate().getTime() + msRemainingAtStartDate)
            },

            startDate() {
                return new Date(Date.UTC(...this.startDateUTC))
            },


        }
        console.log('before init');
        climateClock.init();
        console.log('after init');
    }

});
