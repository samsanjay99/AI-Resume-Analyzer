// Portfolio Template Generator
// This utility helps populate the portfolio template with actual resume data

class PortfolioTemplateGenerator {
    constructor() {
        this.placeholders = {
            // Personal Information
            '{{FULL_NAME}}': '',
            '{{FIRST_NAME}}': '',
            '{{EMAIL}}': '',
            '{{PHONE}}': '',
            '{{LOCATION}}': '',
            '{{LINKEDIN_URL}}': '',
            '{{GITHUB_URL}}': '',
            '{{TWITTER_URL}}': '',
            '{{RESUME_DOWNLOAD_LINK}}': '',
            
            // Professional Information
            '{{JOB_TITLE}}': '',
            '{{CURRENT_POSITION}}': '',
            '{{PROFESSIONAL_SUMMARY}}': '',
            '{{ABOUT_DESCRIPTION}}': '',
            '{{CONTACT_MESSAGE}}': '',
            
            // Statistics
            '{{YEARS_EXPERIENCE}}': '',
            '{{PROJECT_COUNT}}': '',
            '{{SKILL_COUNT}}': '',
            
            // Education
            '{{EDUCATION_DEGREE}}': '',
            '{{EDUCATION_HISTORY}}': '',
            
            // Skills (will be generated as HTML)
            '{{PRIMARY_SKILLS}}': '',
            '{{PROGRAMMING_LANGUAGES}}': '',
            '{{FRAMEWORKS}}': '',
            '{{DATABASES_TOOLS}}': '',
            '{{CLOUD_DEVOPS}}': '',
            
            // Experience (will be generated as HTML)
            '{{WORK_EXPERIENCE}}': '',
            
            // Projects (will be generated as HTML)
            '{{PROJECTS_LIST}}': '',
            
            // Typewriter titles
            '{{SECONDARY_TITLE_1}}': '',
            '{{SECONDARY_TITLE_2}}': '',
            '{{SECONDARY_TITLE_3}}': ''
        };
    }

    // Generate skill items HTML
    generateSkillItems(skills) {
        return skills.map(skill => `
            <div class="skill-item">
                <div class="skill-icon">
                    <i class="${this.getSkillIcon(skill)}"></i>
                </div>
                <div class="skill-name">${skill}</div>
            </div>
        `).join('');
    }

    // Get appropriate icon for skill
    getSkillIcon(skill) {
        const iconMap = {
            // Programming Languages
            'JavaScript': 'fab fa-js-square',
            'Python': 'fab fa-python',
            'Java': 'fab fa-java',
            'C++': 'fas fa-code',
            'C#': 'fas fa-code',
            'PHP': 'fab fa-php',
            'Ruby': 'fas fa-gem',
            'Go': 'fas fa-code',
            'Rust': 'fas fa-code',
            'TypeScript': 'fas fa-code',
            
            // Frameworks
            'React': 'fab fa-react',
            'Angular': 'fab fa-angular',
            'Vue': 'fab fa-vuejs',
            'Node.js': 'fab fa-node-js',
            'Express': 'fas fa-server',
            'Django': 'fas fa-code',
            'Flask': 'fas fa-code',
            'Spring': 'fas fa-leaf',
            'Laravel': 'fas fa-code',
            
            // Databases
            'MySQL': 'fas fa-database',
            'PostgreSQL': 'fas fa-database',
            'MongoDB': 'fas fa-database',
            'Redis': 'fas fa-database',
            'SQLite': 'fas fa-database',
            
            // Cloud & DevOps
            'AWS': 'fab fa-aws',
            'Azure': 'fas fa-cloud',
            'Google Cloud': 'fab fa-google',
            'Docker': 'fab fa-docker',
            'Kubernetes': 'fas fa-dharmachakra',
            'Jenkins': 'fas fa-tools',
            'Git': 'fab fa-git-alt',
            'GitHub': 'fab fa-github',
            
            // Default
            'default': 'fas fa-code'
        };
        
        return iconMap[skill] || iconMap['default'];
    }

    // Generate timeline items for experience
    generateExperienceTimeline(experiences) {
        return experiences.map((exp, index) => `
            <div class="timeline-item">
                <div class="timeline-content">
                    <h3 class="timeline-title">${exp.position}</h3>
                    <h4 class="timeline-company">${exp.company}</h4>
                    <p class="timeline-description">${exp.description}</p>
                </div>
                <div class="timeline-date">${exp.startDate} - ${exp.endDate}</div>
            </div>
        `).join('');
    }

    // Generate timeline items for education
    generateEducationTimeline(education) {
        return education.map((edu, index) => `
            <div class="timeline-item">
                <div class="timeline-content">
                    <h3 class="timeline-title">${edu.degree}</h3>
                    <h4 class="timeline-company">${edu.institution}</h4>
                    <p class="timeline-description">${edu.description || 'Relevant coursework and achievements'}</p>
                </div>
                <div class="timeline-date">${edu.year}</div>
            </div>
        `).join('');
    }

    // Generate project cards
    generateProjectCards(projects) {
        return projects.map(project => `
            <div class="project-card">
                <div class="project-image">
                    <i class="${project.icon || 'fas fa-laptop-code'}"></i>
                </div>
                <div class="project-content">
                    <h3 class="project-title">${project.name}</h3>
                    <p class="project-description">${project.description}</p>
                    <div class="project-tech">
                        ${project.technologies.map(tech => `<span class="tech-tag">${tech}</span>`).join('')}
                    </div>
                    <div class="project-links">
                        ${project.liveUrl ? `<a href="${project.liveUrl}" class="project-link" target="_blank">
                            <i class="fas fa-external-link-alt"></i> Live Demo
                        </a>` : ''}
                        ${project.githubUrl ? `<a href="${project.githubUrl}" class="project-link" target="_blank">
                            <i class="fab fa-github"></i> Source Code
                        </a>` : ''}
                    </div>
                </div>
            </div>
        `).join('');
    }

    // Populate template with resume data
    populateTemplate(templateContent, resumeData) {
        let populatedContent = templateContent;

        // Basic information
        this.placeholders['{{FULL_NAME}}'] = resumeData.personalInfo?.fullName || 'Your Name';
        this.placeholders['{{FIRST_NAME}}'] = resumeData.personalInfo?.firstName || 'Your';
        this.placeholders['{{EMAIL}}'] = resumeData.personalInfo?.email || 'your.email@example.com';
        this.placeholders['{{PHONE}}'] = resumeData.personalInfo?.phone || '+1 (555) 123-4567';
        this.placeholders['{{LOCATION}}'] = resumeData.personalInfo?.location || 'Your City, Country';
        this.placeholders['{{LINKEDIN_URL}}'] = resumeData.socialLinks?.linkedin || 'https://linkedin.com/in/yourprofile';
        this.placeholders['{{GITHUB_URL}}'] = resumeData.socialLinks?.github || 'https://github.com/yourusername';
        this.placeholders['{{TWITTER_URL}}'] = resumeData.socialLinks?.twitter || 'https://twitter.com/yourusername';
        this.placeholders['{{RESUME_DOWNLOAD_LINK}}'] = resumeData.resumeUrl || '#';

        // Professional information
        this.placeholders['{{JOB_TITLE}}'] = resumeData.professionalInfo?.currentTitle || 'Software Developer';
        this.placeholders['{{CURRENT_POSITION}}'] = resumeData.professionalInfo?.currentPosition || 'Software Developer';
        this.placeholders['{{PROFESSIONAL_SUMMARY}}'] = resumeData.professionalInfo?.summary || 'Passionate developer with expertise in modern web technologies and a love for creating innovative solutions.';
        this.placeholders['{{ABOUT_DESCRIPTION}}'] = resumeData.about?.description || 'I am a dedicated software developer with a passion for creating efficient, scalable, and user-friendly applications. With experience in various technologies and frameworks, I enjoy tackling complex problems and turning ideas into reality.';
        this.placeholders['{{CONTACT_MESSAGE}}'] = resumeData.contact?.message || 'I\'m always interested in new opportunities and exciting projects. Whether you have a question or just want to say hi, feel free to reach out!';

        // Statistics
        this.placeholders['{{YEARS_EXPERIENCE}}'] = resumeData.stats?.yearsExperience || '3';
        this.placeholders['{{PROJECT_COUNT}}'] = resumeData.stats?.projectCount || '15';
        this.placeholders['{{SKILL_COUNT}}'] = resumeData.skills ? Object.values(resumeData.skills).flat().length : '20';

        // Education
        this.placeholders['{{EDUCATION_DEGREE}}'] = resumeData.education?.[0]?.degree || 'Bachelor\'s Degree';
        this.placeholders['{{EDUCATION_HISTORY}}'] = resumeData.education ? 
            this.generateEducationTimeline(resumeData.education) : 
            '<div class="timeline-item"><div class="timeline-content"><h3 class="timeline-title">Your Education</h3><h4 class="timeline-company">Your Institution</h4><p class="timeline-description">Add your educational background</p></div><div class="timeline-date">Year</div></div>';

        // Skills
        this.placeholders['{{PRIMARY_SKILLS}}'] = resumeData.skills?.primary?.join(', ') || 'JavaScript, Python, React, Node.js';
        this.placeholders['{{PROGRAMMING_LANGUAGES}}'] = resumeData.skills?.programmingLanguages ? 
            this.generateSkillItems(resumeData.skills.programmingLanguages) : 
            this.generateSkillItems(['JavaScript', 'Python', 'Java', 'TypeScript']);
        this.placeholders['{{FRAMEWORKS}}'] = resumeData.skills?.frameworks ? 
            this.generateSkillItems(resumeData.skills.frameworks) : 
            this.generateSkillItems(['React', 'Node.js', 'Express', 'Django']);
        this.placeholders['{{DATABASES_TOOLS}}'] = resumeData.skills?.databases ? 
            this.generateSkillItems(resumeData.skills.databases) : 
            this.generateSkillItems(['MySQL', 'MongoDB', 'PostgreSQL', 'Redis']);
        this.placeholders['{{CLOUD_DEVOPS}}'] = resumeData.skills?.cloudDevops ? 
            this.generateSkillItems(resumeData.skills.cloudDevops) : 
            this.generateSkillItems(['AWS', 'Docker', 'Git', 'Jenkins']);

        // Experience
        this.placeholders['{{WORK_EXPERIENCE}}'] = resumeData.experience ? 
            this.generateExperienceTimeline(resumeData.experience) : 
            '<div class="timeline-item"><div class="timeline-content"><h3 class="timeline-title">Your Position</h3><h4 class="timeline-company">Your Company</h4><p class="timeline-description">Add your work experience details</p></div><div class="timeline-date">Start - End</div></div>';

        // Projects
        this.placeholders['{{PROJECTS_LIST}}'] = resumeData.projects ? 
            this.generateProjectCards(resumeData.projects) : 
            this.generateProjectCards([
                {
                    name: 'Sample Project',
                    description: 'A brief description of your project and its key features.',
                    technologies: ['React', 'Node.js', 'MongoDB'],
                    icon: 'fas fa-laptop-code',
                    liveUrl: '#',
                    githubUrl: '#'
                }
            ]);

        // Typewriter titles
        this.placeholders['{{SECONDARY_TITLE_1}}'] = resumeData.typewriterTitles?.[0] || 'Full Stack Developer';
        this.placeholders['{{SECONDARY_TITLE_2}}'] = resumeData.typewriterTitles?.[1] || 'Problem Solver';
        this.placeholders['{{SECONDARY_TITLE_3}}'] = resumeData.typewriterTitles?.[2] || 'Tech Enthusiast';

        // Replace all placeholders
        for (const [placeholder, value] of Object.entries(this.placeholders)) {
            populatedContent = populatedContent.replace(new RegExp(placeholder, 'g'), value);
        }

        return populatedContent;
    }

    // Generate complete portfolio from resume data
    generatePortfolio(resumeData) {
        // This would typically read the template file
        // For now, return the populated data structure
        return {
            html: this.populateTemplate('', resumeData),
            css: '', // CSS remains the same
            js: '', // JS remains the same
            placeholders: this.placeholders
        };
    }

    // Get list of all available placeholders
    getAvailablePlaceholders() {
        return Object.keys(this.placeholders);
    }

    // Validate resume data structure
    validateResumeData(resumeData) {
        const requiredFields = ['personalInfo', 'professionalInfo'];
        const missingFields = requiredFields.filter(field => !resumeData[field]);
        
        if (missingFields.length > 0) {
            throw new Error(`Missing required fields: ${missingFields.join(', ')}`);
        }
        
        return true;
    }
}

// Example usage and data structure
const exampleResumeData = {
    personalInfo: {
        fullName: 'John Doe',
        firstName: 'John',
        email: 'john.doe@example.com',
        phone: '+1 (555) 123-4567',
        location: 'San Francisco, CA'
    },
    socialLinks: {
        linkedin: 'https://linkedin.com/in/johndoe',
        github: 'https://github.com/johndoe',
        twitter: 'https://twitter.com/johndoe'
    },
    professionalInfo: {
        currentTitle: 'Senior Full Stack Developer',
        currentPosition: 'Senior Full Stack Developer at Tech Corp',
        summary: 'Passionate full-stack developer with 5+ years of experience building scalable web applications and leading development teams.'
    },
    about: {
        description: 'I am a dedicated software developer with a passion for creating efficient, scalable, and user-friendly applications. With experience in various technologies and frameworks, I enjoy tackling complex problems and turning ideas into reality.'
    },
    stats: {
        yearsExperience: '5',
        projectCount: '25',
    },
    skills: {
        primary: ['JavaScript', 'Python', 'React', 'Node.js'],
        programmingLanguages: ['JavaScript', 'Python', 'Java', 'TypeScript', 'Go'],
        frameworks: ['React', 'Node.js', 'Express', 'Django', 'Vue.js'],
        databases: ['MySQL', 'MongoDB', 'PostgreSQL', 'Redis'],
        cloudDevops: ['AWS', 'Docker', 'Kubernetes', 'Git', 'Jenkins']
    },
    experience: [
        {
            position: 'Senior Full Stack Developer',
            company: 'Tech Corp',
            startDate: '2022',
            endDate: 'Present',
            description: 'Led development of scalable web applications serving 100k+ users. Implemented microservices architecture and improved system performance by 40%.'
        },
        {
            position: 'Full Stack Developer',
            company: 'StartupXYZ',
            startDate: '2020',
            endDate: '2022',
            description: 'Developed and maintained multiple client projects using React, Node.js, and MongoDB. Collaborated with design team to implement responsive UI/UX.'
        }
    ],
    education: [
        {
            degree: 'Bachelor of Science in Computer Science',
            institution: 'University of Technology',
            year: '2020',
            description: 'Graduated Magna Cum Laude with focus on software engineering and algorithms.'
        }
    ],
    projects: [
        {
            name: 'E-Commerce Platform',
            description: 'Full-featured e-commerce platform with payment integration, inventory management, and admin dashboard.',
            technologies: ['React', 'Node.js', 'MongoDB', 'Stripe'],
            icon: 'fas fa-shopping-cart',
            liveUrl: 'https://example-ecommerce.com',
            githubUrl: 'https://github.com/johndoe/ecommerce'
        },
        {
            name: 'Task Management App',
            description: 'Collaborative task management application with real-time updates and team collaboration features.',
            technologies: ['Vue.js', 'Express', 'Socket.io', 'PostgreSQL'],
            icon: 'fas fa-tasks',
            liveUrl: 'https://example-tasks.com',
            githubUrl: 'https://github.com/johndoe/taskapp'
        }
    ],
    typewriterTitles: ['Full Stack Developer', 'Problem Solver', 'Tech Enthusiast', 'Team Leader'],
    contact: {
        message: 'I\'m always interested in new opportunities and exciting projects. Whether you have a question or just want to say hi, feel free to reach out!'
    },
    resumeUrl: './assets/resume.pdf'
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { PortfolioTemplateGenerator, exampleResumeData };
} else {
    window.PortfolioTemplateGenerator = PortfolioTemplateGenerator;
    window.exampleResumeData = exampleResumeData;
}