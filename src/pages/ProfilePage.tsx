import React from 'react';
import { LogOut, Mail, Shield, User as UserIcon } from 'lucide-react';
import { PageContainer } from '../components/layout/PageContainer';
import { Section } from '../components/layout/Section';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { useAuth } from '../hooks/useAuth';

export function ProfilePage() {
  const { currentUser, signOut } = useAuth();

  return (
    <PageContainer size="md">
      <Section
        title="Clinician Account Profile"
        description="Authenticated session information and cloud authorization state."
      >
        <Card>
          <CardHeader>
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-full bg-[#E6F3EF] text-[#087F5B] flex items-center justify-center font-bold text-lg">
                {currentUser?.email ? currentUser.email[0].toUpperCase() : 'U'}
              </div>
              <div>
                <CardTitle className="text-lg">{currentUser?.displayName || 'Registered Clinician'}</CardTitle>
                <CardDescription>{currentUser?.email}</CardDescription>
              </div>
            </div>
          </CardHeader>

          <CardContent className="space-y-4 pt-2">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="p-3 rounded-lg border border-slate-200 bg-slate-50 space-y-1">
                <span className="text-[11px] font-semibold text-[#65756F] uppercase tracking-wider">
                  Firebase UID
                </span>
                <p className="text-xs font-mono text-[#12231E] break-all">{currentUser?.uid}</p>
              </div>

              <div className="p-3 rounded-lg border border-slate-200 bg-slate-50 space-y-1">
                <span className="text-[11px] font-semibold text-[#65756F] uppercase tracking-wider">
                  Auth Status
                </span>
                <div>
                  <Badge variant="success" size="sm" hasDot>
                    Verified Identity
                  </Badge>
                </div>
              </div>
            </div>
          </CardContent>

          <CardFooter className="border-t border-slate-100 justify-between">
            <span className="text-xs text-[#65756F]">Session secured with Google Cloud Identity</span>
            <Button
              size="sm"
              variant="outline"
              leftIcon={<LogOut className="w-3.5 h-3.5" />}
              onClick={() => signOut()}
            >
              Sign Out
            </Button>
          </CardFooter>
        </Card>
      </Section>
    </PageContainer>
  );
}
