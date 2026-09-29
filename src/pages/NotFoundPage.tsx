import React from 'react';
import { Link } from 'react-router-dom';
import { FileQuestion, Home } from 'lucide-react';
import { PageContainer } from '../components/layout/PageContainer';
import { Button } from '../components/ui/Button';

export function NotFoundPage() {
  return (
    <PageContainer size="sm" className="py-20 flex items-center justify-center flex-1">
      <div className="text-center space-y-4 max-w-md">
        <div className="w-14 h-14 rounded-2xl bg-slate-100 text-slate-500 mx-auto flex items-center justify-center">
          <FileQuestion className="w-8 h-8 stroke-[1.5]" />
        </div>
        <h1 className="text-2xl font-bold text-[#12231E]">Page Not Found</h1>
        <p className="text-xs text-[#65756F] leading-relaxed">
          The requested route does not exist or has been relocated within the CardioPulse clinical
          intelligence environment.
        </p>
        <div className="pt-2">
          <Link to="/">
            <Button size="md" variant="primary" leftIcon={<Home className="w-4 h-4" />}>
              Return to Overview
            </Button>
          </Link>
        </div>
      </div>
    </PageContainer>
  );
}
