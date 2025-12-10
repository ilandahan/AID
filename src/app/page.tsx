import { Typography } from '@/components/atoms/Typography';
import { Button } from '@/components/atoms/Button';
import styles from './page.module.css';

export default function HomePage() {
  return (
    <main className={styles.main}>
      <section className={styles.hero}>
        <Typography variant="h1">
          AID
        </Typography>
        <Typography variant="body-lg" color="secondary">
          AI Development Methodology
        </Typography>
        <Typography variant="body" color="muted" className={styles.tagline}>
          Structure First. Humans Lead. Nothing Lost.
        </Typography>
        
        <div className={styles.actions}>
          <Button 
            label="Get Started" 
            variant="primary" 
            size="lg"
          />
          <Button 
            label="Documentation" 
            variant="secondary" 
            size="lg"
          />
        </div>
      </section>

      <section className={styles.phases}>
        <Typography variant="h2">The 5-Phase Workflow</Typography>
        
        <div className={styles.phaseGrid}>
          <div className={styles.phase}>
            <Typography variant="h3">1. Discovery</Typography>
            <Typography variant="body-sm" color="secondary">
              Understand the problem deeply before proposing solutions.
            </Typography>
          </div>
          
          <div className={styles.phase}>
            <Typography variant="h3">2. PRD</Typography>
            <Typography variant="body-sm" color="secondary">
              Define what to build with clear requirements and acceptance criteria.
            </Typography>
          </div>
          
          <div className={styles.phase}>
            <Typography variant="h3">3. Tech Spec</Typography>
            <Typography variant="body-sm" color="secondary">
              Design the architecture and technical approach.
            </Typography>
          </div>
          
          <div className={styles.phase}>
            <Typography variant="h3">4. Development</Typography>
            <Typography variant="body-sm" color="secondary">
              Implement using TDD with tests first, always.
            </Typography>
          </div>
          
          <div className={styles.phase}>
            <Typography variant="h3">5. QA & Ship</Typography>
            <Typography variant="body-sm" color="secondary">
              Validate quality and deploy with confidence.
            </Typography>
          </div>
        </div>
      </section>

      <section className={styles.principles}>
        <Typography variant="h2">Core Principles</Typography>
        
        <div className={styles.principleGrid}>
          <div className={styles.principle}>
            <Typography variant="h4">Humans Lead</Typography>
            <Typography variant="body-sm" color="secondary">
              AI accelerates, humans decide. Every phase gate requires human approval.
            </Typography>
          </div>
          
          <div className={styles.principle}>
            <Typography variant="h4">Structure First</Typography>
            <Typography variant="body-sm" color="secondary">
              Clarity before code. Each phase builds on documented foundations.
            </Typography>
          </div>
          
          <div className={styles.principle}>
            <Typography variant="h4">Nothing Lost</Typography>
            <Typography variant="body-sm" color="secondary">
              Context persists, knowledge compounds. Resume exactly where you left off.
            </Typography>
          </div>
        </div>
      </section>
    </main>
  );
}
