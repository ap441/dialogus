import { AuthPanel } from "@/components/AuthPanel";
import { Navbar } from "@/components/Navbar";

export default function SignupPage() {
  return (
    <main className="screen backdrop">
      <Navbar compact />
      <div className="center-wrap">
        <AuthPanel mode="signup" />
      </div>
    </main>
  );
}
