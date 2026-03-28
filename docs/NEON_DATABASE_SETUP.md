# 🗄️ Neon Database Setup for Learning Dashboard

## Quick Setup (5 minutes)

### Step 1: Access Neon SQL Editor
1. Go to https://console.neon.tech/
2. Login to your account
3. Select your project (the one connected to your app)
4. Click on "SQL Editor" in the left sidebar

### Step 2: Run the SQL Script
1. Copy the entire content from `scripts/create_learning_tables.sql`
2. Paste it into the Neon SQL Editor
3. Click "Run" button (or press Ctrl+Enter)
4. Wait for execution to complete (~5 seconds)

### Step 3: Verify Tables Created
You should see output like:
```
✅ 2 tables created
✅ 15 courses seeded
✅ Learning Dashboard tables created and seeded successfully!
```

### Step 4: Test in Your App
1. Go to your Streamlit app
2. Perform a resume analysis
3. Check the Learning Dashboard
4. You should now see course recommendations! 🎉

---

## What This Script Does

### Creates 2 Tables:

1. **course_recommendations**
   - Stores personalized course recommendations for each user
   - Links to user_id, resume_id, and analysis_id
   - Tracks watch progress and bookmarks

2. **skill_course_mapping**
   - Master list of available courses for each skill
   - Contains 15 popular YouTube courses
   - Skills covered: Python, SQL, JavaScript, React, Java, ML, Data Science, AWS, Docker, Git, Node.js, Angular, MongoDB, Kubernetes, TypeScript

### Creates 4 Indexes:
- Fast lookup by user_id
- Fast lookup by skill
- Fast lookup by platform
- Fast lookup by skill_name

### Seeds 15 Courses:
All courses are from trusted sources:
- freeCodeCamp.org
- Programming with Mosh
- TechWorld with Nana
- Web Dev Simplified

---

## Troubleshooting

### Error: "relation already exists"
✅ This is fine! It means the tables already exist. The script uses `CREATE TABLE IF NOT EXISTS` so it's safe to run multiple times.

### Error: "permission denied"
❌ Make sure you're using the correct database connection string with write permissions.

### No courses showing in app
1. Check if tables exist:
   ```sql
   SELECT COUNT(*) FROM skill_course_mapping;
   ```
   Should return 15

2. Check if recommendations are being saved:
   ```sql
   SELECT COUNT(*) FROM course_recommendations;
   ```
   Should increase after each analysis

3. Restart your Streamlit app

---

## Manual Verification Queries

### Check table structure:
```sql
\d course_recommendations
\d skill_course_mapping
```

### View all available courses:
```sql
SELECT skill_name, course_title, channel_name 
FROM skill_course_mapping 
ORDER BY skill_name;
```

### View your recommendations:
```sql
SELECT u.email, cr.skill_covered, cr.course_title 
FROM course_recommendations cr
JOIN users u ON cr.user_id = u.id
ORDER BY cr.recommended_date DESC;
```

### Check indexes:
```sql
SELECT indexname, tablename 
FROM pg_indexes 
WHERE tablename IN ('course_recommendations', 'skill_course_mapping');
```

---

## Adding More Courses

You can add more courses manually:

```sql
INSERT INTO skill_course_mapping 
(skill_name, course_title, youtube_video_id, thumbnail_url, 
 channel_name, video_duration, course_url, difficulty_level)
VALUES
('YourSkill', 'Course Title', 'VIDEO_ID', 
 'https://img.youtube.com/vi/VIDEO_ID/maxresdefault.jpg',
 'Channel Name', 'Duration', 
 'https://youtube.com/watch?v=VIDEO_ID', 'Beginner');
```

---

## Database Schema

### course_recommendations
| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL | Primary key |
| user_id | INTEGER | User who received recommendation |
| resume_id | INTEGER | Resume that was analyzed |
| analysis_id | INTEGER | Analysis that generated recommendation |
| course_title | TEXT | Course name |
| course_platform | TEXT | Platform (YouTube) |
| skill_covered | TEXT | Skill this course teaches |
| youtube_video_id | TEXT | YouTube video ID |
| thumbnail_url | TEXT | Course thumbnail |
| channel_name | TEXT | YouTube channel |
| video_duration | TEXT | Course length |
| course_url | TEXT | Full YouTube URL |
| is_watched | BOOLEAN | User watched status |
| is_bookmarked | BOOLEAN | User bookmark status |
| watch_progress | INTEGER | Progress percentage |
| recommended_date | TIMESTAMP | When recommended |

### skill_course_mapping
| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL | Primary key |
| skill_name | TEXT | Skill name |
| course_title | TEXT | Course name |
| youtube_video_id | TEXT | YouTube video ID |
| thumbnail_url | TEXT | Course thumbnail |
| channel_name | TEXT | YouTube channel |
| video_duration | TEXT | Course length |
| course_url | TEXT | Full YouTube URL |
| difficulty_level | TEXT | Beginner/Intermediate/Advanced |
| rating | REAL | Course rating (0-5) |
| view_count | INTEGER | Number of views |
| created_at | TIMESTAMP | When added |

---

## Success Checklist

After running the script, verify:

- [ ] Tables created without errors
- [ ] 15 courses seeded in skill_course_mapping
- [ ] Indexes created successfully
- [ ] Verification queries return data
- [ ] App can query tables without errors
- [ ] Resume analysis generates recommendations
- [ ] Learning Dashboard displays courses

---

## Next Steps

1. ✅ Run the SQL script in Neon
2. ✅ Verify tables exist
3. ✅ Test resume analysis
4. ✅ Check Learning Dashboard
5. 🎉 Enjoy personalized course recommendations!

---

**Need Help?**
- Check Neon logs for errors
- Verify DATABASE_URL in Streamlit secrets
- Restart Streamlit app after creating tables
- Check app logs for any errors
