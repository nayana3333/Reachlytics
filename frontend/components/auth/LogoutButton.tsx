"use client";

import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/Button";
import { clearToken } from "@/lib/api";

export function LogoutButton() {
  const router = useRouter();

  return (
    <Button
      variant="secondary"
      onClick={() => {
        clearToken();
        router.push("/login");
      }}
    >
      Log out
    </Button>
  );
}
