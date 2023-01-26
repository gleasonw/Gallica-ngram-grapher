import React, { ReactNode } from "react";
import Link from "next/link";
import Image from "next/image";

export const BaseLayout: React.FC<{ children: ReactNode }> = ({ children }) => {
  return (
    <div className="h-screen w-screen flex flex-col">
      <div className={"flex flex-row justify-between m-5"}>
        <Link href="/" className={"text-3xl self-start"}>
          📊
        </Link>
        <div className={"flex flex-row gap-5 align-center justify-center"}>
          <Link href="/info">
            <Image src={"/info.svg"} width={40} height={40} alt={"Info page"} />
          </Link>
          <Link
            href={"https://github.com/gleasonw/gallica-grapher"}
            target={"_blank"}
          >
            <Image src={"/github.svg"} width={40} height={40} alt={"Github"} />
          </Link>
          <Link
            target={"_blank"}
            href="https://github.com/gleasonw/gallica-grapher/issues"
            className={"text-center self-center w-10"}
          >
            Report bug
          </Link>
        </div>
      </div>
      {children}
    </div>
  );
};
