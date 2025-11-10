import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { fetchBlogPosts, BlogPost } from '../lib/api';

const InsightsSection = () => {
  const { t, i18n } = useTranslation();
  const [posts, setPosts] = useState<BlogPost[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchBlogPosts(3)
      .then(setPosts)
      .catch(() => setError(t('errors.failedToLoad')));
  }, [i18n.language, t]);

  return (
    <section id="insights">
      <div className="container">
        <h2 style={{ textAlign: 'center', marginBottom: '3rem', fontSize: '2.2rem' }}>{t('insights.title')}</h2>
        {error && <p className="text-muted" style={{ textAlign: 'center' }}>{error}</p>}
        <div className="grid columns-3">
          {posts.length === 0 && !error && (
            <div className="card" style={{ gridColumn: '1 / -1', textAlign: 'center' }}>
              <p className="text-muted">{t('insights.empty')}</p>
            </div>
          )}
          {posts.map((post) => (
            <article key={post.id} className="card">
              <h3 style={{ marginBottom: '0.75rem' }}>{post.title}</h3>
              {post.summary && <p className="text-muted">{post.summary}</p>}
              <a className="secondary" href={`/blog/${post.slug}`}>{t('common.readMore')}</a>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
};

export default InsightsSection;
