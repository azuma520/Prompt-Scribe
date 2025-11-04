// /lib/utils.ts
import clsx, { type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

/** 合併 className 並自動處理 Tailwind 衝突 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

