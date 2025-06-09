import React from "react";

export function InfoCard({ title, value }: { title: string; value: string }) {
    return (
        <>
            <div
                style={{
                    display: "flex",
                    flexDirection: "column",
                    flexWrap: "nowrap",
                    justifyContent: "space-between",
                    backgroundColor: "var(--card)",
                    zIndex: 2001,
                    color: "var(--color-foreground)",
                    border: "none",
                    maxWidth: "1250px",
                    width: "calc(100% - 70%)",
                    padding: "30px",
                    borderRadius: "4px",
                }}
            >
                <span className="roboto-text text-2xl">{title}</span>
                <span
                    style={{ fontStyle: "bold" }}
                    className="roboto-heading text-2xl text-black font-extrabold"
                >
                    {value}
                </span>
            </div>
        </>
    );
}
