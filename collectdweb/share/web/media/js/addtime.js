define(function() {
    "use strict";
    var _times = {
        minute: 60,
        hour: 60*60,
        day: 24*60*60,
        week: 7*24*60*60,
        month: 31*24*60*60,
        year: 365.25*24*60*60
    };
    var addTime = function( date, interval, timespan) {
        if ( timespan === undefined ) {
            return new Date( date.getTime() + interval);
        } else {
            return new Date( date.getTime() + interval * 1000 * _times[timespan] );
        }
    };
    return addTime;
});
