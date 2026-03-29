-- ============================================================================
-- Add More Popular Courses from Various Channels
-- Run this in Neon SQL Editor to add more course options
-- ============================================================================

INSERT INTO skill_course_mapping 
(skill_name, course_title, youtube_video_id, thumbnail_url, channel_name, video_duration, course_url, difficulty_level)
VALUES
    -- HTML/CSS
    ('HTML', 'HTML Tutorial for Beginners', 'qz0aGYrrlhU', 
     'https://img.youtube.com/vi/qz0aGYrrlhU/maxresdefault.jpg',
     'Programming with Mosh', '1:00:41', 
     'https://youtube.com/watch?v=qz0aGYrrlhU', 'Beginner'),
    
    ('CSS', 'CSS Tutorial for Beginners', 'yfoY53QXEnI',
     'https://img.youtube.com/vi/yfoY53QXEnI/maxresdefault.jpg',
     'Programming with Mosh', '1:11:37',
     'https://youtube.com/watch?v=yfoY53QXEnI', 'Beginner'),
    
    -- Responsive Design
    ('Responsive Design', 'Responsive Web Design Tutorial', 'srvUrASNj0s',
     'https://img.youtube.com/vi/srvUrASNj0s/maxresdefault.jpg',
     'freeCodeCamp.org', '4:25:00',
     'https://youtube.com/watch?v=srvUrASNj0s', 'Beginner'),
    
    -- Testing
    ('Testing', 'JavaScript Testing Tutorial', 'FgnxcUQ5vho',
     'https://img.youtube.com/vi/FgnxcUQ5vho/maxresdefault.jpg',
     'freeCodeCamp.org', '1:36:00',
     'https://youtube.com/watch?v=FgnxcUQ5vho', 'Intermediate'),
    
    ('Testing Frameworks', 'Jest Testing Tutorial', 'IPiUDhwnZxA',
     'https://img.youtube.com/vi/IPiUDhwnZxA/maxresdefault.jpg',
     'Codevolution', '2:38:00',
     'https://youtube.com/watch?v=IPiUDhwnZxA', 'Intermediate'),
    
    -- State Management
    ('State Management', 'Redux Tutorial for Beginners', 'poQXNp9ItL4',
     'https://img.youtube.com/vi/poQXNp9ItL4/maxresdefault.jpg',
     'Programming with Mosh', '1:01:54',
     'https://youtube.com/watch?v=poQXNp9ItL4', 'Intermediate'),
    
    -- API/REST
    ('API', 'REST API Tutorial', 'SLwpqD8n3d0',
     'https://img.youtube.com/vi/SLwpqD8n3d0/maxresdefault.jpg',
     'Programming with Mosh', '1:13:07',
     'https://youtube.com/watch?v=SLwpqD8n3d0', 'Beginner'),
    
    ('RESTful API', 'Build a REST API with Node.js', 'fgTGADljAeg',
     'https://img.youtube.com/vi/fgTGADljAeg/maxresdefault.jpg',
     'Programming with Mosh', '1:03:17',
     'https://youtube.com/watch?v=fgTGADljAeg', 'Intermediate'),
    
    -- Deployment
    ('Deployment', 'Deploy Web Apps Tutorial', 'l134cBAJCuc',
     'https://img.youtube.com/vi/l134cBAJCuc/maxresdefault.jpg',
     'freeCodeCamp.org', '1:11:28',
     'https://youtube.com/watch?v=l134cBAJCuc', 'Intermediate'),
    
    -- Debugging
    ('Debugging', 'Chrome DevTools Tutorial', 'x4q86IjJFag',
     'https://img.youtube.com/vi/x4q86IjJFag/maxresdefault.jpg',
     'freeCodeCamp.org', '1:23:00',
     'https://youtube.com/watch?v=x4q86IjJFag', 'Beginner'),
    
    -- CodeWithHarry Courses
    ('Python', 'Python Tutorial in Hindi', 'gfDE2a7MKjA',
     'https://img.youtube.com/vi/gfDE2a7MKjA/maxresdefault.jpg',
     'CodeWithHarry', '13:44:00',
     'https://youtube.com/watch?v=gfDE2a7MKjA', 'Beginner'),
    
    ('JavaScript', 'JavaScript Tutorial in Hindi', 'ER9SspLe4Hg',
     'https://img.youtube.com/vi/ER9SspLe4Hg/maxresdefault.jpg',
     'CodeWithHarry', '6:00:00',
     'https://youtube.com/watch?v=ER9SspLe4Hg', 'Beginner'),
    
    ('React', 'React JS Tutorial in Hindi', 'RGKi6LSPDLU',
     'https://img.youtube.com/vi/RGKi6LSPDLU/maxresdefault.jpg',
     'CodeWithHarry', '2:33:00',
     'https://youtube.com/watch?v=RGKi6LSPDLU', 'Beginner'),
    
    ('Web Development', 'Web Development Course', 'tVzUXW6siu0',
     'https://img.youtube.com/vi/tVzUXW6siu0/maxresdefault.jpg',
     'CodeWithHarry', '13:16:00',
     'https://youtube.com/watch?v=tVzUXW6siu0', 'Beginner'),
    
    ('HTML', 'HTML Tutorial in Hindi', 'BsDoLVMnmZs',
     'https://img.youtube.com/vi/BsDoLVMnmZs/maxresdefault.jpg',
     'CodeWithHarry', '2:33:00',
     'https://youtube.com/watch?v=BsDoLVMnmZs', 'Beginner'),
    
    ('CSS', 'CSS Tutorial in Hindi', 'Edsxf_NBFrw',
     'https://img.youtube.com/vi/Edsxf_NBFrw/maxresdefault.jpg',
     'CodeWithHarry', '4:00:00',
     'https://youtube.com/watch?v=Edsxf_NBFrw', 'Beginner'),
    
    -- More popular channels
    ('Python', 'Python for Everybody', 'eWRfhZUzrAc',
     'https://img.youtube.com/vi/eWRfhZUzrAc/maxresdefault.jpg',
     'freeCodeCamp.org', '13:26:00',
     'https://youtube.com/watch?v=eWRfhZUzrAc', 'Beginner'),
    
    ('Data Structures', 'Data Structures and Algorithms', 'RBSGKlAvoiM',
     'https://img.youtube.com/vi/RBSGKlAvoiM/maxresdefault.jpg',
     'freeCodeCamp.org', '5:00:00',
     'https://youtube.com/watch?v=RBSGKlAvoiM', 'Intermediate'),
    
    ('Problem Solving', 'Problem Solving Techniques', '8ext9G7xspg',
     'https://img.youtube.com/vi/8ext9G7xspg/maxresdefault.jpg',
     'freeCodeCamp.org', '3:00:00',
     'https://youtube.com/watch?v=8ext9G7xspg', 'Intermediate')

ON CONFLICT (skill_name, youtube_video_id) DO NOTHING;

-- Verify new courses
SELECT skill_name, COUNT(*) as course_count 
FROM skill_course_mapping 
GROUP BY skill_name 
ORDER BY course_count DESC, skill_name;

SELECT '✅ Added more courses from popular channels!' as status;
