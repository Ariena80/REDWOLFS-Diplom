<?php
header('Content-Type: application/json');

// Подключение к базе данных
$servername = "DESKTOP-DCFTGAQ\SQLEXPRESS02";
$username = "arien";
$password = "12345678";
$dbname = "FIZORGER-DB";

$conn = new mysqli($servername, $username, $password, $dbname);

if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// Функция для получения данных пользователя
function getUserData($conn, $user_id) {
    $sql = "SELECT full_name, date_of_birth, profile_picture FROM users WHERE id = $user_id";
    $result = $conn->query($sql);
    if ($result->num_rows > 0) {
        return $result->fetch_assoc();
    } else {
        return null;
    }
}

// Функция для обновления профиля пользователя
function updateProfile($conn, $user_id, $full_name, $date_of_birth, $profile_picture) {
    $sql = "UPDATE users SET full_name = '$full_name', date_of_birth = '$date_of_birth', profile_picture = '$profile_picture' WHERE id = $user_id";
    return $conn->query($sql);
}

// Функция для загрузки файлов
function uploadFiles($files, $upload_dir) {
    $file_paths = [];
    foreach ($files['name'] as $key => $name) {
        $tmp_name = $files['tmp_name'][$key];
        $file_path = $upload_dir . basename($name);
        move_uploaded_file($tmp_name, $file_path);
        $file_paths[] = $file_path;
    }
    return $file_paths;
}

// Функция для добавления команды
function addTeam($conn, $team_name, $course, $sport_type, $gender, $team_members, $reserve_member) {
    $sql = "INSERT INTO teams (team_name, course, sport_type, gender, team_members, reserve_member) VALUES ('$team_name', '$course', '$sport_type', '$gender', '$team_members', '$reserve_member')";
    return $conn->query($sql);
}

// Функция для добавления физорга
function addPhysOrg($conn, $last_name, $first_name, $middle_name, $gender, $course, $group, $login, $password) {
    $sql = "INSERT INTO physorgs (last_name, first_name, middle_name, gender, course, group, login, password) VALUES ('$last_name', '$first_name', '$middle_name', '$gender', '$course', '$group', '$login', '$password')";
    return $conn->query($sql);
}

// Функция для добавления мероприятия
function addEvent($conn, $event_type, $sport_type, $gender, $event_name, $event_date, $event_time, $location) {
    $sql = "INSERT INTO events (event_type, sport_type, gender, event_name, event_date, event_time, location) VALUES ('$event_type', '$sport_type', '$gender', '$event_name', '$event_date', '$event_time', '$location')";
    return $conn->query($sql);
}

// Функция для редактирования расписания тренировок
function editSchedule($conn, $sport_type_schedule, $training_date, $training_time, $coach_name) {
    $sql = "UPDATE training_schedule SET sport_type_schedule = '$sport_type_schedule', training_date = '$training_date', training_time = '$training_time', coach_name = '$coach_name' WHERE id = 1";
    return $conn->query($sql);
}

// Функция для добавления новости
function addNews($conn, $news_title, $news_content, $file_path) {
    $sql = "INSERT INTO news (news_title, news_content, news_image) VALUES ('$news_title', '$news_content', '$file_path')";
    return $conn->query($sql);
}

// Функция для добавления награды
function addAward($conn, $award_name, $recipient, $file_path) {
    $sql = "INSERT INTO awards (award_name, recipient, award_image) VALUES ('$award_name', '$recipient', '$file_path')";
    return $conn->query($sql);
}

// Обработка запросов
$method = $_SERVER['REQUEST_METHOD'];
$request_uri = $_SERVER['REQUEST_URI'];

switch ($request_uri) {
    case '/api/login':
        if ($method === 'POST') {
            $data = json_decode(file_get_contents('php://input'), true);
            $login = $data['login'];
            $password = $data['password'];
            $user = User.query.filter_by(login=$login, password=$password).first();
            if ($user) {
                echo json_encode(array('success' => true, 'message' => 'Login successful'));
            } else {
                echo json_encode(array('success' => false, 'message' => 'Invalid login or password'));
            }
        }
        break;

    case '/api/update_profile':
        if ($method === 'POST') {
            $user_id = 1; // Предполагается, что ID пользователя известен
            $full_name = $_POST['full_name'];
            $date_of_birth = $_POST['date_of_birth'];
            $profile_picture = $_FILES['profile_picture']['name'];
            if (updateProfile($conn, $user_id, $full_name, $date_of_birth, $profile_picture)) {
                echo json_encode(array('success' => true, 'message' => 'Profile updated successfully'));
            } else {
                echo json_encode(array('success' => false, 'message' => 'Error updating profile'));
            }
        }
        break;

    case '/api/upload':
        if ($method === 'POST') {
            $title = $_POST['title'];
            $course = $_POST['course'];
            $sport_type = $_POST['sport_type'];
            $media_files = $_FILES['media_files'];
            $upload_dir = 'uploads/';
            $file_paths = uploadFiles($media_files, $upload_dir);
            if ($file_paths) {
                echo json_encode(array('success' => true, 'message' => 'Media uploaded successfully'));
            } else {
                echo json_encode(array('success' => false, 'message' => 'Error uploading media'));
            }
        }
        break;

    case '/api/add_team':
        if ($method === 'POST') {
            $team_name = $_POST['team_name'];
            $course = $_POST['course'];
            $sport_type = $_POST['sport_type'];
            $gender = $_POST['gender'];
            $team_members = $_POST['team_members'];
            $reserve_member = $_POST['reserve_member'];
            if (addTeam($conn, $team_name, $course, $sport_type, $gender, $team_members, $reserve_member)) {
                echo json_encode(array('success' => true, 'message' => 'Team added successfully'));
            } else {
                echo json_encode(array('success' => false, 'message' => 'Error adding team'));
            }
        }
        break;

    case '/api/add_physorg':
        if ($method === 'POST') {
            $last_name = $_POST['last_name'];
            $first_name = $_POST['first_name'];
            $middle_name = $_POST['middle_name'];
            $gender = $_POST['gender'];
            $course = $_POST['course'];
            $group = $_POST['group'];
            $login = $_POST['login'];
            $password = $_POST['password'];
            if (addPhysOrg($conn, $last_name, $first_name, $middle_name, $gender, $course, $group, $login, $password)) {
                echo json_encode(array('success' => true, 'message' => 'Physorg added successfully'));
            } else {
                echo json_encode(array('success' => false, 'message' => 'Error adding physorg'));
            }
        }
        break;

    case '/api/add_event':
        if ($method === 'POST') {
            $event_type = $_POST['event_type'];
            $sport_type = $_POST['sport_type'];
            $gender = $_POST['gender'];
            $event_name = $_POST['event_name'];
            $event_date = $_POST['event_date'];
            $event_time = $_POST['event_time'];
            $location = $_POST['location'];
            if (addEvent($conn, $event_type, $sport_type, $gender, $event_name, $event_date, $event_time, $location)) {
                echo json_encode(array('success' => true, 'message' => 'Event added successfully'));
            } else {
                echo json_encode(array('success' => false, 'message' => 'Error adding event'));
            }
        }
        break;

    case '/api/edit_schedule':
        if ($method === 'POST') {
            $sport_type_schedule = $_POST['sport_type_schedule'];
            $training_date = $_POST['training_date'];
            $training_time = $_POST['training_time'];
            $coach_name = $_POST['coach_name'];
            if (editSchedule($conn, $sport_type_schedule, $training_date, $training_time, $coach_name)) {
                echo json_encode(array('success' => true, 'message' => 'Schedule updated successfully'));
            } else {
                echo json_encode(array('success' => false, 'message' => 'Error updating schedule'));
            }
        }
        break;

    case '/api/add_news':
        if ($method === 'POST') {
            $news_title = $_POST['news_title'];
            $news_content = $_POST['news_content'];
            $news_images = $_FILES['news_image'];
            $upload_dir = 'uploads/';
            $file_paths = uploadFiles($news_images, $upload_dir);
            if (addNews($conn, $news_title, $news_content, $file_paths[0])) {
                echo json_encode(array('success' => true, 'message' => 'News added successfully'));
            } else {
                echo json_encode(array('success' => false, 'message' => 'Error adding news'));
            }
        }
        break;

    case '/api/add_award':
        if ($method === 'POST') {
            $award_name = $_POST['award_name'];
            $recipient = $_POST['recipient'];
            $award_image = $_FILES['award_image'];
            $upload_dir = 'uploads/';
            $file_paths = uploadFiles($award_image, $upload_dir);
            if (addAward($conn, $award_name, $recipient, $file_paths[0])) {
                echo json_encode(array('success' => true, 'message' => 'Award added successfully'));
            } else {
                echo json_encode(array('success' => false, 'message' => 'Error adding award'));
            }
        }
        break;

    default:
        echo json_encode(array('success' => false, 'message' => 'Invalid request'));
        break;
}

$conn->close();
?>