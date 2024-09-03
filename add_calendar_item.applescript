tell application "Calendar"
   tell calendar "School"
      set startDate to date "{_start}"
      set endDate to date "{_end}"
      make new event at end with properties {{description:"{_description}", summary:"{_title}", location:"{_location}", start date:startDate, end date:endDate}}
   end tell
end tell