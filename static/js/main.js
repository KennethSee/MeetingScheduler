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

    // Set Days of the week to check to weekdays only on click of weekdayOnlyButton
    document.frm.weekdayOnlyButton.onclick = function(){
        $("#MondayCheck").prop("checked", true);
        $("#TuesdayCheck").prop("checked", true);
        $("#WednesdayCheck").prop("checked", true);
        $("#ThursdayCheck").prop("checked", true);
        $("#FridayCheck").prop("checked", true);
        $("#SaturdayCheck").prop("checked", false);
        $("#SundayCheck").prop("checked", false);
    }

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
        // Validate that at least one day of the week is checked
        if(document.getElementById("MondayCheck").checked == false 
            && document.getElementById("TuesdayCheck").checked == false
            && document.getElementById("WednesdayCheck").checked == false
            && document.getElementById("ThursdayCheck").checked == false
            && document.getElementById("FridayCheck").checked == false
            && document.getElementById("SaturdayCheck").checked == false
            && document.getElementById("SundayCheck").checked == false
        )
        {
            alert("At least one day of the week has to be selected!");
            return false;
        }
        return true;
    }
});