import Image from "next/image";
import glassIcon from "./assets/glass.svg";

export default function InputBubble(props: {
  word: string;
  onWordChange: (word: string) => void;
  onSubmit?: () => void;
  children?: React.ReactNode;
}) {
  return (
    <div className="text-2xl relative w-full max-w-3xl">
      <input
        className={"p-5 w-full rounded-3xl border-2 hover:shadow-lg"}
        placeholder={"rechercher un mot"}
        value={props.word || ""}
        onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
          props.onWordChange(e.target.value)
        }
        onKeyPress={(e: React.KeyboardEvent<HTMLInputElement>) => {
          if (e.key === "Enter" && props.onSubmit) {
            props.onSubmit();
          }
        }}
      />
      {props.children}
    </div>
  );
}
