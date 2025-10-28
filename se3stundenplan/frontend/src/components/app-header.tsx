import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "./ui/dropdown-menu";
import { Button } from "./ui/button";
import { useSession, signOut } from "next-auth/react";
import { ArrowLeft, LogOut, User } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/router";

export default function AppHeader() {
  const { data: session } = useSession();
  const router = useRouter();

  if (!session) return null;

  const isRoot = router.pathname === "/";

  return (
    <header className="mt-4 flex items-center justify-between">
      <div>
        {!isRoot && (
          <Button variant="outline" size="icon" onClick={() => router.back()}>
            <ArrowLeft />
          </Button>
        )}
      </div>
      <div>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button
              size="icon"
              variant="outline"
              className="cursor-pointer size-12 rounded-full"
            >
              <User size="24" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuLabel className="flex flex-col">
              {session?.user.name}
              <span className="text-xs text-muted-foreground">
                {session?.user.email}
              </span>
            </DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem>
              <Link className="inline-flex items-center gap-2" href="/profile">
                <User /> Profil
              </Link>
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => signOut()}>
              <LogOut /> Ausloggen
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
}
