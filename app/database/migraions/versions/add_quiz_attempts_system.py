"""add quiz attempts system

Revision ID: mno345pqr678
Revises: ghi789jkl012
Create Date: 2025-08-01

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa



revision = "mno345pqr678"
down_revision = "ghi789jkl012"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create quiz_attempts table
    op.create_table('quiz_attempts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('quiz_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('finished_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('score', sa.Integer(), server_default=sa.text('0'), nullable=False),
        sa.Column('attempt_no', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['quiz_id'], ['quizzes.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('quiz_id', 'user_id', 'attempt_no', name='uq_quiz_user_attempt')
    )
    
    # Add attempt_id column to answers table
    op.add_column('answers', sa.Column('attempt_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_answers_attempt', 'answers', 'quiz_attempts', ['attempt_id'], ['id'], ondelete='CASCADE')
    
    # For existing data: create default attempts and link answers
    # This is a data migration - in production you'd need to handle existing data carefully
    op.execute("""
        -- Create default attempts for existing answers
        WITH existing_user_quizzes AS (
            SELECT DISTINCT a.user_id, q.quiz_id, MIN(a.created_at) as first_answer_at
            FROM answers a
            JOIN questions q ON a.question_id = q.id
            WHERE a.deleted_at IS NULL
            GROUP BY a.user_id, q.quiz_id
        )
        INSERT INTO quiz_attempts (user_id, quiz_id, attempt_no, started_at, finished_at, score)
        SELECT 
            user_id, 
            quiz_id, 
            1 as attempt_no,
            first_answer_at as started_at,
            first_answer_at as finished_at,  -- Mark as finished since they're existing
            0 as score  -- Default score, will need recalculation
        FROM existing_user_quizzes;
    """)
    
    # Link existing answers to their attempts
    op.execute("""
        UPDATE answers 
        SET attempt_id = qa.id
        FROM quiz_attempts qa
        JOIN questions q ON qa.quiz_id = q.quiz_id
        WHERE answers.question_id = q.id 
        AND answers.user_id = qa.user_id
        AND qa.attempt_no = 1
        AND answers.deleted_at IS NULL;
    """)
    
    # Now make attempt_id NOT NULL since all answers should have attempts
    op.alter_column('answers', 'attempt_id', nullable=False)
    
    # Remove user_id from answers since we now use attempt_id
    op.drop_constraint('answers_user_id_fkey', 'answers', type_='foreignkey')
    op.drop_column('answers', 'user_id')


def downgrade() -> None:
    # Add user_id back to answers
    op.add_column('answers', sa.Column('user_id', sa.Integer(), nullable=True))
    
    # Populate user_id from attempt relationship
    op.execute("""
        UPDATE answers 
        SET user_id = qa.user_id
        FROM quiz_attempts qa
        WHERE answers.attempt_id = qa.id;
    """)
    
    # Make user_id NOT NULL and add foreign key
    op.alter_column('answers', 'user_id', nullable=False)
    op.create_foreign_key('answers_user_id_fkey', 'answers', 'users', ['user_id'], ['id'])
    
    # Remove attempt_id from answers
    op.drop_constraint('fk_answers_attempt', 'answers', type_='foreignkey')
    op.drop_column('answers', 'attempt_id')
    
    # Drop quiz_attempts table
    op.drop_table('quiz_attempts')