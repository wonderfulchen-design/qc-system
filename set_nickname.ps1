$token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwidXNlcm5hbWUiOiJhZG1pbiIsInJvbGUiOiJhZG1pbiIsImV4cCI6MTc3NDY3MTQ0M30.EG0m0EYqmGrFvpZOEUPQn8CWJktJ2elG6bW6adzZCcI"
$headers = @{
    Authorization = "Bearer $token"
    "Content-Type" = "application/json"
}
$body = @{nickname = "小虾"} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8000/api/user/nickname" -Method Put -Headers $headers -Body $body
$response | ConvertTo-Json
