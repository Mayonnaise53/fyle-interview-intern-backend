-- Write query to find the number of grade A's given by the teacher who has graded the most assignments
WITH TeacherAssignmentCounts AS (
    SELECT 
        teacher_id,
        COUNT(*) AS total_assignments
    FROM assignments
    WHERE state = 'GRADED'  -- Only count graded assignments
    GROUP BY teacher_id
),
TopTeacher AS (
    SELECT 
        teacher_id
    FROM TeacherAssignmentCounts
    ORDER BY total_assignments DESC
    LIMIT 1
)
SELECT 
    COUNT(*) AS grade_a_count
FROM assignments
WHERE teacher_id = (SELECT teacher_id FROM TopTeacher)
  AND grade = 'A';  -- Make sure 'A' matches your enum value for grade A
