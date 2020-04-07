var StartingDateTime = new Date();
var EndingDateTime = new Date();

var client_id = new String("3b25d750-9b21-4793-91cf-298e839932bf");

var UserTimeZone = new String();


document.addEventListener("DOMContentLoaded", function(){
    // Set form default values
    UserTimeZone = Intl.DateTimeFormat().resolvedOptions().timeZone
    document.getElementById("TimeWindowStart").defaultValue = "09:00";
    document.getElementById("TimeWindowEnd").defaultValue = "17:00";
    document.getElementById("TimeInterval").defaultValue = "15";
    $(function() {
        var temp=UserTimeZone; 
        $("#TimeZoneMain").val(temp);
    });

    // Perform submission validations
    document.frm.submit.onclick = function(){
        StartingDateTime = document.frm.StartingDate.value.concat(" ", document.frm.StartingTime.value, ":00");
        EndingDateTime = document.frm.EndingDate.value.concat(" ", document.frm.EndingTime.value, ":00");
        // Validate that ending date is the same or after starting date
        if(StartingDateTime > EndingDateTime)
        {
            alert("Ending time cannot be earlier than Starting time!");
            return false;
        }
        return true;
    }
});