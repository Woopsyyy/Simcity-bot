=== PATCH NOTES ===
[2024-06-24]
- Improved folder selection logic for ZIP backups:
  - The script now scans all folders for the current date and fills any missing ZIP slots (1-100) in order, starting from the lowest group number.
  - Only when all folders for today are full (100 ZIPs each) will a new folder be created for additional backups.
  - Folders from previous dates are not affected; only today's folders are filled.
==================== 
